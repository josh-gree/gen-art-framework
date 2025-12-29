"""Distribution sampling for parameter spaces."""

from __future__ import annotations

from typing import Any

import numpy as np
import scipy.stats

from gen_art_framework.schema import ParameterSpace


def sample_parameter_space(
    space: ParameterSpace, rng: np.random.Generator
) -> dict[str, Any]:
    """Sample values from a parameter space.

    Args:
        space: The parameter space to sample from.
        rng: A numpy random generator for reproducible sampling.

    Returns:
        A dictionary mapping parameter names to sampled values.

    Raises:
        ValueError: If a distribution name is unknown.
    """
    result = {}

    for param in space:
        result[param.name] = _sample_distribution(
            param.distribution, param.args, rng
        )

    return result


def _sample_distribution(
    distribution: str, args: dict[str, Any], rng: np.random.Generator
) -> Any:
    """Sample a single value from a distribution.

    Args:
        distribution: The name of the distribution.
        args: Arguments to pass to the distribution.
        rng: A numpy random generator.

    Returns:
        A sampled value.

    Raises:
        ValueError: If the distribution name is unknown.
    """
    # Handle special cases
    if distribution == "constant":
        if "value" not in args:
            raise ValueError("'constant' distribution requires a 'value' argument.")
        return args["value"]

    if distribution == "choice":
        if "values" not in args:
            raise ValueError("'choice' distribution requires a 'values' argument.")
        values = args["values"]
        if not values:
            raise ValueError("'choice' distribution requires a non-empty 'values' list.")
        weights = args.get("weights")
        if weights is not None and len(weights) != len(values):
            raise ValueError(
                f"'choice' distribution 'weights' length ({len(weights)}) "
                f"must match 'values' length ({len(values)})."
            )
        idx = rng.choice(len(values), p=weights)
        return values[idx]

    # Look up scipy distribution
    dist = getattr(scipy.stats, distribution, None)
    if dist is None or not isinstance(
        dist, (scipy.stats.rv_continuous, scipy.stats.rv_discrete)
    ):
        raise ValueError(
            f"Unknown distribution '{distribution}'. "
            f"Must be 'constant', 'choice', or a valid scipy.stats distribution."
        )

    return dist.rvs(random_state=rng, **args)
