"""Tests for parameter space sampling."""

from textwrap import dedent

import numpy as np
import pytest

from gen_art_framework import parse_parameter_space, sample_parameter_space


class TestDeterministicSampling:
    """Tests for deterministic sampling with seeded RNG."""

    def test_same_seed_produces_same_values(self):
        """Same seed produces identical samples."""
        docstring = dedent("""
            parameters:
              - name: x
                distribution: uniform
                loc: 0
                scale: 100
        """)
        space = parse_parameter_space(docstring)

        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)

        result1 = sample_parameter_space(space, rng1)
        result2 = sample_parameter_space(space, rng2)

        assert result1["x"] == result2["x"]

    def test_different_seeds_produce_different_values(self):
        """Different seeds produce different samples."""
        docstring = dedent("""
            parameters:
              - name: x
                distribution: uniform
                loc: 0
                scale: 100
        """)
        space = parse_parameter_space(docstring)

        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(999)

        result1 = sample_parameter_space(space, rng1)
        result2 = sample_parameter_space(space, rng2)

        assert result1["x"] != result2["x"]


class TestScipyDistributions:
    """Tests for scipy.stats distributions."""

    def test_uniform_distribution(self):
        """Samples from uniform distribution."""
        docstring = dedent("""
            parameters:
              - name: x
                distribution: uniform
                loc: 0
                scale: 1
        """)
        space = parse_parameter_space(docstring)
        rng = np.random.default_rng(42)

        result = sample_parameter_space(space, rng)

        assert 0 <= result["x"] <= 1

    def test_norm_distribution(self):
        """Samples from normal distribution."""
        docstring = dedent("""
            parameters:
              - name: x
                distribution: norm
                loc: 100
                scale: 0.001
        """)
        space = parse_parameter_space(docstring)
        rng = np.random.default_rng(42)

        result = sample_parameter_space(space, rng)

        assert 99 < result["x"] < 101

    def test_randint_distribution(self):
        """Samples from discrete uniform distribution."""
        docstring = dedent("""
            parameters:
              - name: n
                distribution: randint
                low: 1
                high: 10
        """)
        space = parse_parameter_space(docstring)
        rng = np.random.default_rng(42)

        result = sample_parameter_space(space, rng)

        assert 1 <= result["n"] < 10
        assert isinstance(result["n"], (int, np.integer))

    def test_beta_distribution(self):
        """Samples from beta distribution."""
        docstring = dedent("""
            parameters:
              - name: x
                distribution: beta
                a: 2
                b: 5
        """)
        space = parse_parameter_space(docstring)
        rng = np.random.default_rng(42)

        result = sample_parameter_space(space, rng)

        assert 0 <= result["x"] <= 1

    def test_poisson_distribution(self):
        """Samples from Poisson distribution."""
        docstring = dedent("""
            parameters:
              - name: k
                distribution: poisson
                mu: 5
        """)
        space = parse_parameter_space(docstring)
        rng = np.random.default_rng(42)

        result = sample_parameter_space(space, rng)

        assert result["k"] >= 0
        assert isinstance(result["k"], (int, np.integer))


class TestConstantDistribution:
    """Tests for constant distribution."""

    def test_constant_returns_fixed_value(self):
        """Constant distribution returns the fixed value."""
        docstring = dedent("""
            parameters:
              - name: seed
                distribution: constant
                value: 42
        """)
        space = parse_parameter_space(docstring)
        rng = np.random.default_rng(0)

        result = sample_parameter_space(space, rng)

        assert result["seed"] == 42

    def test_constant_with_string_value(self):
        """Constant distribution works with string values."""
        docstring = dedent("""
            parameters:
              - name: mode
                distribution: constant
                value: "debug"
        """)
        space = parse_parameter_space(docstring)
        rng = np.random.default_rng(0)

        result = sample_parameter_space(space, rng)

        assert result["mode"] == "debug"

    def test_constant_ignores_rng(self):
        """Constant distribution returns same value regardless of RNG state."""
        docstring = dedent("""
            parameters:
              - name: x
                distribution: constant
                value: 123
        """)
        space = parse_parameter_space(docstring)

        rng1 = np.random.default_rng(1)
        rng2 = np.random.default_rng(9999)

        result1 = sample_parameter_space(space, rng1)
        result2 = sample_parameter_space(space, rng2)

        assert result1["x"] == result2["x"] == 123


class TestChoiceDistribution:
    """Tests for choice distribution."""

    def test_choice_selects_from_values(self):
        """Choice distribution selects from the provided values."""
        docstring = dedent("""
            parameters:
              - name: colour
                distribution: choice
                values: ["red", "green", "blue"]
        """)
        space = parse_parameter_space(docstring)
        rng = np.random.default_rng(42)

        result = sample_parameter_space(space, rng)

        assert result["colour"] in ["red", "green", "blue"]

    def test_choice_deterministic_with_seed(self):
        """Choice distribution is deterministic with same seed."""
        docstring = dedent("""
            parameters:
              - name: colour
                distribution: choice
                values: ["red", "green", "blue"]
        """)
        space = parse_parameter_space(docstring)

        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)

        result1 = sample_parameter_space(space, rng1)
        result2 = sample_parameter_space(space, rng2)

        assert result1["colour"] == result2["colour"]

    def test_choice_with_numeric_values(self):
        """Choice distribution works with numeric values."""
        docstring = dedent("""
            parameters:
              - name: size
                distribution: choice
                values: [10, 20, 30, 40]
        """)
        space = parse_parameter_space(docstring)
        rng = np.random.default_rng(42)

        result = sample_parameter_space(space, rng)

        assert result["size"] in [10, 20, 30, 40]


class TestUnknownDistribution:
    """Tests for unknown distribution error handling."""

    def test_unknown_distribution_raises_value_error(self):
        """Unknown distribution raises ValueError with helpful message."""
        docstring = dedent("""
            parameters:
              - name: x
                distribution: not_a_real_distribution
        """)
        space = parse_parameter_space(docstring)
        rng = np.random.default_rng(42)

        with pytest.raises(ValueError) as excinfo:
            sample_parameter_space(space, rng)

        assert "not_a_real_distribution" in str(excinfo.value)
        assert "scipy.stats" in str(excinfo.value)


class TestMultipleParameters:
    """Tests for sampling multiple parameters at once."""

    def test_samples_all_parameters(self):
        """Samples all parameters in the space."""
        docstring = dedent("""
            parameters:
              - name: x
                distribution: uniform
                loc: 0
                scale: 1
              - name: mode
                distribution: constant
                value: "test"
              - name: colour
                distribution: choice
                values: ["red", "blue"]
        """)
        space = parse_parameter_space(docstring)
        rng = np.random.default_rng(42)

        result = sample_parameter_space(space, rng)

        assert "x" in result
        assert "mode" in result
        assert "colour" in result
        assert 0 <= result["x"] <= 1
        assert result["mode"] == "test"
        assert result["colour"] in ["red", "blue"]
