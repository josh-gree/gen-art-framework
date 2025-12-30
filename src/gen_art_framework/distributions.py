"""Distribution sampling for parameter spaces."""

from __future__ import annotations

from typing import Any

import numpy as np
import scipy.stats

from gen_art_framework.schema import ParameterSpace


class ConstantDistribution:
    """Wrapper for constant distribution with scipy-like interface."""

    def __init__(self, value: Any):
        """Create a constant distribution that always returns the same value.

        Args:
            value: The constant value to return.
        """
        self._value = value

    def rvs(self, size=None):
        """Sample from the constant distribution.

        Args:
            size: Optional size parameter (ignored, returns scalar or array of constant).

        Returns:
            The constant value, or array of constant values if size is specified.
        """
        if size is None:
            return self._value
        return np.full(size, self._value)


class ChoiceDistribution:
    """Wrapper for choice distribution with scipy-like interface."""

    def __init__(self, values: list, weights: list | None, rng: np.random.Generator):
        """Create a choice distribution that samples from a set of values.

        Args:
            values: List of values to choose from.
            weights: Optional list of weights (must match length of values).
            rng: Numpy random generator for sampling.
        """
        self._values = values
        self._weights = weights
        self._rng = rng

    def rvs(self, size=None):
        """Sample from the choice distribution.

        Args:
            size: Optional size parameter for number of samples.

        Returns:
            A single sampled value, or array of sampled values if size is specified.
        """
        if size is None:
            idx = self._rng.choice(len(self._values), p=self._weights)
            return self._values[idx]
        indices = self._rng.choice(len(self._values), size=size, p=self._weights)
        return np.array([self._values[i] for i in indices])


class ScipyDistributionWrapper:
    """Wrapper for scipy distributions with fixed RNG."""

    def __init__(self, frozen_dist, rng: np.random.Generator):
        """Create a scipy distribution wrapper with fixed RNG.

        Args:
            frozen_dist: A frozen scipy distribution (created with dist(**args)).
            rng: Numpy random generator for sampling.
        """
        self._frozen_dist = frozen_dist
        self._rng = rng

    def rvs(self, size=None):
        """Sample from the scipy distribution.

        Args:
            size: Optional size parameter for number of samples.

        Returns:
            A single sampled value, or array of sampled values if size is specified.
        """
        return self._frozen_dist.rvs(size=size, random_state=self._rng)


def sample_parameter_space(
    space: ParameterSpace, rng: np.random.Generator
) -> dict[str, Any]:
    """Sample values from a parameter space.

    Args:
        space: The parameter space to sample from.
        rng: A numpy random generator for reproducible sampling.

    Returns:
        A dictionary mapping parameter names to sampled values or distribution objects.
        When a parameter has mode="distribution", the value will be a distribution object
        with a .rvs() method instead of a sampled value.

    Raises:
        ValueError: If a distribution name is unknown.
    """
    result = {}

    for param in space:
        result[param.name] = _sample_distribution(
            param.distribution, param.args, rng, mode=param.mode
        )

    return result


def _sample_distribution(
    distribution: str,
    args: dict[str, Any],
    rng: np.random.Generator,
    mode: str = "sample",
) -> Any:
    """Sample a single value from a distribution or return a frozen distribution object.

    Args:
        distribution: The name of the distribution.
        args: Arguments to pass to the distribution.
        rng: A numpy random generator.
        mode: Either "sample" (returns a sampled value) or "distribution" (returns a distribution object).

    Returns:
        A sampled value (if mode="sample") or a distribution object with .rvs() method (if mode="distribution").

    Raises:
        ValueError: If the distribution name is unknown.
    """
    # Handle special cases
    if distribution == "constant":
        if "value" not in args:
            raise ValueError("'constant' distribution requires a 'value' argument.")
        value = args["value"]
        if mode == "distribution":
            return ConstantDistribution(value)
        return value

    if distribution == "choice":
        if "values" not in args:
            raise ValueError("'choice' distribution requires a 'values' argument.")
        values = args["values"]
        if not values:
            raise ValueError(
                "'choice' distribution requires a non-empty 'values' list."
            )
        weights = args.get("weights")
        if weights is not None and len(weights) != len(values):
            raise ValueError(
                f"'choice' distribution 'weights' length ({len(weights)}) "
                f"must match 'values' length ({len(values)})."
            )
        if mode == "distribution":
            return ChoiceDistribution(values, weights, rng)
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

    if mode == "distribution":
        frozen_dist = dist(**args)
        return ScipyDistributionWrapper(frozen_dist, rng)

    return dist.rvs(random_state=rng, **args)
