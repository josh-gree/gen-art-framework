from importlib.metadata import version

from gen_art_framework.cli import cli
from gen_art_framework.distributions import sample_parameter_space
from gen_art_framework.executor import execute_script
from gen_art_framework.schema import (
    ParameterDefinition,
    ParameterSpace,
    parse_parameter_space,
)


__version__ = version("gen-art-framework")


def hello() -> str:
    return "Hello from gen-art-framework!"


__all__ = [
    "__version__",
    "ParameterDefinition",
    "ParameterSpace",
    "cli",
    "execute_script",
    "parse_parameter_space",
    "sample_parameter_space",
    "hello",
]
