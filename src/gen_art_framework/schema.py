"""Parameter space schema definitions and YAML parsing."""

from __future__ import annotations

import builtins
import keyword
from dataclasses import dataclass
from typing import Any

import yaml

# Names that would shadow Python builtins or cause issues when injected as globals
RESERVED_PARAMETER_NAMES = frozenset(dir(builtins)) | frozenset(keyword.kwlist)


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

    The docstring must be raw YAML starting with 'parameters:' on the first line.
    """
    if not docstring:
        raise ValueError("Docstring is empty")

    content = docstring.strip()

    # First line must start with 'parameters:'
    first_line = content.split("\n")[0].strip()
    if not first_line.startswith("parameters:"):
        raise ValueError("Docstring must start with 'parameters:'")

    return content


def _validate_parameter(param_dict: dict[str, Any]) -> ParameterDefinition:
    """Validate and convert a parameter dict to ParameterDefinition.

    Only validates structure (name and distribution fields required).
    Distribution-specific validation is handled by the distributions module.
    """
    if not isinstance(param_dict, dict):
        raise ValueError("Parameter definition must be a mapping")
    if "name" not in param_dict:
        raise ValueError("Parameter definition missing 'name' field")
    if "distribution" not in param_dict:
        raise ValueError(f"Parameter '{param_dict['name']}' missing 'distribution' field")

    name = param_dict["name"]
    distribution = param_dict["distribution"]

    if not isinstance(name, str):
        raise ValueError(f"Parameter 'name' must be a string, got {type(name).__name__}")
    if not isinstance(distribution, str):
        raise ValueError(f"Parameter '{name}' 'distribution' must be a string, got {type(distribution).__name__}")

    if name in RESERVED_PARAMETER_NAMES:
        raise ValueError(
            f"Parameter name '{name}' is reserved (shadows a Python builtin or keyword)"
        )

    # Extract args (everything except name and distribution)
    args = {k: v for k, v in param_dict.items() if k not in ("name", "distribution")}

    return ParameterDefinition(name=name, distribution=distribution, args=args)


def parse_parameter_space(docstring: str) -> ParameterSpace:
    """Parse a docstring containing YAML parameter definitions into a ParameterSpace.

    Args:
        docstring: A docstring containing YAML starting with 'parameters:' on the
                   first line.

    Returns:
        A ParameterSpace containing the parsed parameter definitions.

    Raises:
        ValueError: If the docstring doesn't start with 'parameters:', the YAML is
                    malformed, required fields are missing, or parameter names are
                    duplicated.
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

    if len(data["parameters"]) == 0:
        raise ValueError("'parameters' must not be empty")

    # Validate and convert each parameter
    parameters = [_validate_parameter(p) for p in data["parameters"]]

    # Check for duplicate names
    names = [p.name for p in parameters]
    duplicates = [name for name in names if names.count(name) > 1]
    if duplicates:
        raise ValueError(f"Duplicate parameter names: {', '.join(sorted(set(duplicates)))}")

    return ParameterSpace(parameters=parameters)
