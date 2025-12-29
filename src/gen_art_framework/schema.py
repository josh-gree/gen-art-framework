"""Parameter space schema definitions and YAML parsing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import yaml


@dataclass
class ParameterDefinition:
    """Definition of a single parameter with its distribution."""

    name: str
    distribution: str
    args: dict[str, Any]


@dataclass
class ParameterSpace:
    """Container for multiple parameter definitions."""

    parameters: list[ParameterDefinition]

    def __iter__(self):
        return iter(self.parameters)

    def __len__(self):
        return len(self.parameters)

    def __getitem__(self, key: str) -> ParameterDefinition:
        for param in self.parameters:
            if param.name == key:
                return param
        raise KeyError(key)


def _extract_yaml_from_docstring(docstring: str) -> str:
    """Extract YAML content from a docstring.

    Handles YAML embedded in markdown code blocks (```yaml ... ```) or raw YAML.
    """
    if not docstring:
        raise ValueError("Docstring is empty")

    # Try to extract from markdown code block first
    # Match ```yaml or ```yml or just ```
    code_block_pattern = r"```(?:ya?ml)?\s*\n(.*?)```"
    match = re.search(code_block_pattern, docstring, re.DOTALL)

    if match:
        return match.group(1).strip()

    # If no code block, try to find raw YAML (look for parameters: key)
    if "parameters:" in docstring:
        # Find the YAML section starting from 'parameters:'
        lines = docstring.split("\n")
        yaml_lines = []
        in_yaml = False

        for line in lines:
            if "parameters:" in line and not in_yaml:
                in_yaml = True
                yaml_lines.append(line)
            elif in_yaml:
                # Stop at empty line followed by non-indented text or end of string
                if line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                    if yaml_lines and not line.startswith("-"):
                        break
                yaml_lines.append(line)

        if yaml_lines:
            return "\n".join(yaml_lines).strip()

    raise ValueError("No YAML content found in docstring")


def _validate_uniform(args: dict[str, Any], name: str) -> None:
    """Validate uniform distribution parameters."""
    if "low" not in args:
        raise ValueError(f"Parameter '{name}': uniform distribution requires 'low' field")
    if "high" not in args:
        raise ValueError(f"Parameter '{name}': uniform distribution requires 'high' field")


def _validate_normal(args: dict[str, Any], name: str) -> None:
    """Validate normal distribution parameters."""
    if "mean" not in args:
        raise ValueError(f"Parameter '{name}': normal distribution requires 'mean' field")
    if "std" not in args:
        raise ValueError(f"Parameter '{name}': normal distribution requires 'std' field")


def _validate_choice(args: dict[str, Any], name: str) -> None:
    """Validate choice distribution parameters."""
    if "values" not in args:
        raise ValueError(f"Parameter '{name}': choice distribution requires 'values' field")
    if not isinstance(args["values"], list):
        raise ValueError(f"Parameter '{name}': choice 'values' must be a list")


def _validate_constant(args: dict[str, Any], name: str) -> None:
    """Validate constant distribution parameters."""
    if "value" not in args:
        raise ValueError(f"Parameter '{name}': constant distribution requires 'value' field")


_VALIDATORS = {
    "uniform": _validate_uniform,
    "normal": _validate_normal,
    "choice": _validate_choice,
    "constant": _validate_constant,
}


def _validate_parameter(param_dict: dict[str, Any]) -> ParameterDefinition:
    """Validate and convert a parameter dict to ParameterDefinition."""
    if "name" not in param_dict:
        raise ValueError("Parameter definition missing 'name' field")
    if "distribution" not in param_dict:
        raise ValueError(f"Parameter '{param_dict['name']}' missing 'distribution' field")

    name = param_dict["name"]
    distribution = param_dict["distribution"]

    if distribution not in _VALIDATORS:
        raise ValueError(
            f"Parameter '{name}': unknown distribution type '{distribution}'. "
            f"Supported types: {', '.join(_VALIDATORS.keys())}"
        )

    # Extract args (everything except name and distribution)
    args = {k: v for k, v in param_dict.items() if k not in ("name", "distribution")}

    # Validate distribution-specific requirements
    _VALIDATORS[distribution](args, name)

    return ParameterDefinition(name=name, distribution=distribution, args=args)


def parse_parameter_space(docstring: str) -> ParameterSpace:
    """Parse a docstring containing YAML parameter definitions into a ParameterSpace.

    Args:
        docstring: A docstring containing YAML parameter definitions, either
                   in a markdown code block or as raw YAML.

    Returns:
        A ParameterSpace containing the parsed parameter definitions.

    Raises:
        ValueError: If the YAML is malformed or missing required fields.
    """
    # Extract YAML content
    yaml_content = _extract_yaml_from_docstring(docstring)

    # Parse YAML
    try:
        data = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        raise ValueError(f"Malformed YAML: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("YAML must be a mapping with 'parameters' key")

    if "parameters" not in data:
        raise ValueError("YAML must contain 'parameters' key")

    if not isinstance(data["parameters"], list):
        raise ValueError("'parameters' must be a list")

    # Validate and convert each parameter
    parameters = [_validate_parameter(p) for p in data["parameters"]]

    return ParameterSpace(parameters=parameters)
