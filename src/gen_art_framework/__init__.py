from gen_art_framework.distributions import sample_parameter_space
from gen_art_framework.schema import (
    ParameterDefinition,
    ParameterSpace,
    parse_parameter_space,
)


def hello() -> str:
    return "Hello from gen-art-framework!"


__all__ = [
    "ParameterDefinition",
    "ParameterSpace",
    "parse_parameter_space",
    "sample_parameter_space",
    "hello",
]
