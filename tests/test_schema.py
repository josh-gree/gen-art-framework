"""Tests for parameter space schema parsing."""

import pytest

from gen_art_framework import parse_parameter_space


class TestYAMLExtraction:
    """Tests for YAML extraction from docstrings."""

    def test_extract_yaml_from_markdown_code_block(self):
        """Extracts YAML from markdown ```yaml blocks."""
        docstring = """
        Some description.

        ```yaml
        parameters:
          - name: x
            distribution: uniform
            low: 0
            high: 1
        ```
        """
        result = parse_parameter_space(docstring)
        assert len(result) == 1
        assert result["x"].name == "x"

    def test_extract_yaml_from_yml_code_block(self):
        """Extracts YAML from markdown ```yml blocks."""
        docstring = """
        ```yml
        parameters:
          - name: y
            distribution: constant
            value: 42
        ```
        """
        result = parse_parameter_space(docstring)
        assert len(result) == 1
        assert result["y"].name == "y"

    def test_extract_yaml_from_plain_code_block(self):
        """Extracts YAML from plain ``` blocks."""
        docstring = """
        ```
        parameters:
          - name: z
            distribution: constant
            value: 10
        ```
        """
        result = parse_parameter_space(docstring)
        assert len(result) == 1

    def test_extract_raw_yaml(self):
        """Extracts raw YAML without code blocks."""
        docstring = """
        parameters:
          - name: alpha
            distribution: uniform
            low: 0.0
            high: 1.0
        """
        result = parse_parameter_space(docstring)
        assert len(result) == 1
        assert result["alpha"].name == "alpha"

    def test_empty_docstring_raises(self):
        """Raises ValueError for empty docstring."""
        with pytest.raises(ValueError, match="empty"):
            parse_parameter_space("")

    def test_no_yaml_raises(self):
        """Raises ValueError when no YAML content found."""
        with pytest.raises(ValueError, match="No YAML content found"):
            parse_parameter_space("Just some text without YAML")


class TestUniformDistribution:
    """Tests for uniform distribution parsing."""

    def test_valid_uniform(self):
        """Parses valid uniform distribution."""
        docstring = """
        ```yaml
        parameters:
          - name: x
            distribution: uniform
            low: 0.0
            high: 10.0
        ```
        """
        result = parse_parameter_space(docstring)
        param = result["x"]
        assert param.distribution == "uniform"
        assert param.args["low"] == 0.0
        assert param.args["high"] == 10.0

    def test_uniform_missing_low_raises(self):
        """Raises ValueError when uniform missing 'low'."""
        docstring = """
        ```yaml
        parameters:
          - name: x
            distribution: uniform
            high: 10.0
        ```
        """
        with pytest.raises(ValueError, match="requires 'low' field"):
            parse_parameter_space(docstring)

    def test_uniform_missing_high_raises(self):
        """Raises ValueError when uniform missing 'high'."""
        docstring = """
        ```yaml
        parameters:
          - name: x
            distribution: uniform
            low: 0.0
        ```
        """
        with pytest.raises(ValueError, match="requires 'high' field"):
            parse_parameter_space(docstring)


class TestNormalDistribution:
    """Tests for normal distribution parsing."""

    def test_valid_normal(self):
        """Parses valid normal distribution."""
        docstring = """
        ```yaml
        parameters:
          - name: noise
            distribution: normal
            mean: 0.0
            std: 1.0
        ```
        """
        result = parse_parameter_space(docstring)
        param = result["noise"]
        assert param.distribution == "normal"
        assert param.args["mean"] == 0.0
        assert param.args["std"] == 1.0

    def test_normal_missing_mean_raises(self):
        """Raises ValueError when normal missing 'mean'."""
        docstring = """
        ```yaml
        parameters:
          - name: x
            distribution: normal
            std: 1.0
        ```
        """
        with pytest.raises(ValueError, match="requires 'mean' field"):
            parse_parameter_space(docstring)

    def test_normal_missing_std_raises(self):
        """Raises ValueError when normal missing 'std'."""
        docstring = """
        ```yaml
        parameters:
          - name: x
            distribution: normal
            mean: 0.0
        ```
        """
        with pytest.raises(ValueError, match="requires 'std' field"):
            parse_parameter_space(docstring)


class TestChoiceDistribution:
    """Tests for choice distribution parsing."""

    def test_valid_choice(self):
        """Parses valid choice distribution."""
        docstring = """
        ```yaml
        parameters:
          - name: colour
            distribution: choice
            values: ["red", "green", "blue"]
        ```
        """
        result = parse_parameter_space(docstring)
        param = result["colour"]
        assert param.distribution == "choice"
        assert param.args["values"] == ["red", "green", "blue"]

    def test_choice_missing_values_raises(self):
        """Raises ValueError when choice missing 'values'."""
        docstring = """
        ```yaml
        parameters:
          - name: x
            distribution: choice
        ```
        """
        with pytest.raises(ValueError, match="requires 'values' field"):
            parse_parameter_space(docstring)

    def test_choice_values_not_list_raises(self):
        """Raises ValueError when choice 'values' is not a list."""
        docstring = """
        ```yaml
        parameters:
          - name: x
            distribution: choice
            values: "not a list"
        ```
        """
        with pytest.raises(ValueError, match="must be a list"):
            parse_parameter_space(docstring)


class TestConstantDistribution:
    """Tests for constant distribution parsing."""

    def test_valid_constant(self):
        """Parses valid constant distribution."""
        docstring = """
        ```yaml
        parameters:
          - name: seed
            distribution: constant
            value: 42
        ```
        """
        result = parse_parameter_space(docstring)
        param = result["seed"]
        assert param.distribution == "constant"
        assert param.args["value"] == 42

    def test_constant_missing_value_raises(self):
        """Raises ValueError when constant missing 'value'."""
        docstring = """
        ```yaml
        parameters:
          - name: x
            distribution: constant
        ```
        """
        with pytest.raises(ValueError, match="requires 'value' field"):
            parse_parameter_space(docstring)


class TestValidationErrors:
    """Tests for validation error handling."""

    def test_malformed_yaml_raises(self):
        """Raises ValueError for malformed YAML."""
        docstring = """
        ```yaml
        parameters:
          - name: x
            distribution: uniform
              bad_indent: here
        ```
        """
        with pytest.raises(ValueError, match="Malformed YAML"):
            parse_parameter_space(docstring)

    def test_missing_name_raises(self):
        """Raises ValueError when parameter missing 'name'."""
        docstring = """
        ```yaml
        parameters:
          - distribution: uniform
            low: 0
            high: 1
        ```
        """
        with pytest.raises(ValueError, match="missing 'name' field"):
            parse_parameter_space(docstring)

    def test_missing_distribution_raises(self):
        """Raises ValueError when parameter missing 'distribution'."""
        docstring = """
        ```yaml
        parameters:
          - name: x
            low: 0
            high: 1
        ```
        """
        with pytest.raises(ValueError, match="missing 'distribution' field"):
            parse_parameter_space(docstring)

    def test_unknown_distribution_raises(self):
        """Raises ValueError for unknown distribution type."""
        docstring = """
        ```yaml
        parameters:
          - name: x
            distribution: unknown_dist
        ```
        """
        with pytest.raises(ValueError, match="unknown distribution type"):
            parse_parameter_space(docstring)

    def test_missing_parameters_key_raises(self):
        """Raises ValueError when YAML missing 'parameters' key."""
        docstring = """
        ```yaml
        something_else:
          - name: x
        ```
        """
        with pytest.raises(ValueError, match="must contain 'parameters' key"):
            parse_parameter_space(docstring)

    def test_parameters_not_list_raises(self):
        """Raises ValueError when 'parameters' is not a list."""
        docstring = """
        ```yaml
        parameters:
          name: x
          distribution: constant
          value: 1
        ```
        """
        with pytest.raises(ValueError, match="must be a list"):
            parse_parameter_space(docstring)


class TestParameterSpace:
    """Tests for ParameterSpace container functionality."""

    def test_iteration(self):
        """ParameterSpace is iterable."""
        docstring = """
        ```yaml
        parameters:
          - name: a
            distribution: constant
            value: 1
          - name: b
            distribution: constant
            value: 2
        ```
        """
        result = parse_parameter_space(docstring)
        names = [p.name for p in result]
        assert names == ["a", "b"]

    def test_len(self):
        """ParameterSpace has length."""
        docstring = """
        ```yaml
        parameters:
          - name: a
            distribution: constant
            value: 1
          - name: b
            distribution: constant
            value: 2
          - name: c
            distribution: constant
            value: 3
        ```
        """
        result = parse_parameter_space(docstring)
        assert len(result) == 3

    def test_getitem_by_name(self):
        """ParameterSpace supports indexing by name."""
        docstring = """
        ```yaml
        parameters:
          - name: first
            distribution: constant
            value: 1
          - name: second
            distribution: constant
            value: 2
        ```
        """
        result = parse_parameter_space(docstring)
        assert result["first"].args["value"] == 1
        assert result["second"].args["value"] == 2

    def test_getitem_unknown_raises(self):
        """ParameterSpace raises KeyError for unknown parameter."""
        docstring = """
        ```yaml
        parameters:
          - name: exists
            distribution: constant
            value: 1
        ```
        """
        result = parse_parameter_space(docstring)
        with pytest.raises(KeyError):
            result["does_not_exist"]


class TestMultipleParameters:
    """Tests for parameter spaces with multiple parameters."""

    def test_multiple_different_distributions(self):
        """Parses multiple parameters with different distributions."""
        docstring = """
        ```yaml
        parameters:
          - name: x
            distribution: uniform
            low: 0
            high: 100
          - name: y
            distribution: normal
            mean: 50
            std: 10
          - name: colour
            distribution: choice
            values: ["red", "blue"]
          - name: seed
            distribution: constant
            value: 42
        ```
        """
        result = parse_parameter_space(docstring)
        assert len(result) == 4
        assert result["x"].distribution == "uniform"
        assert result["y"].distribution == "normal"
        assert result["colour"].distribution == "choice"
        assert result["seed"].distribution == "constant"
