# Distributions

This document covers the available parameter distributions for sampling.

## Built-in Distributions

### `constant`

Returns a fixed value. Useful for dimensions or other values you want consistent across samples.

```yaml
- name: width
  distribution: constant
  value: 800
```

**Arguments:**

- `value` (required) - The value to return (can be any type)

### `choice`

Randomly selects from a list of values.

```yaml
- name: colour
  distribution: choice
  values: ["red", "green", "blue"]
```

**Arguments:**

- `values` (required) - List of values to choose from
- `weights` (optional) - List of weights for each value (must match length of `values` and sum to 1.0)

**Weighted example:**

```yaml
- name: size
  distribution: choice
  values: ["small", "medium", "large"]
  weights: [0.5, 0.3, 0.2]  # 50% small, 30% medium, 20% large
```

### `randint`

Samples a random integer from a range. Uses `scipy.stats.randint`.

```yaml
- name: count
  distribution: randint
  low: 10
  high: 50
```

**Arguments:**

- `low` (required) - Lower bound (inclusive)
- `high` (required) - Upper bound (exclusive)

The sampled value will be in the range `[low, high)`.

### `uniform`

Samples a floating-point value from a uniform distribution. Uses `scipy.stats.uniform`.

```yaml
- name: opacity
  distribution: uniform
  loc: 0.0
  scale: 1.0
```

**Arguments:**

- `loc` (required) - Lower bound (minimum value)
- `scale` (required) - Width of the distribution (not the upper bound!)

The sampled value will be in the range `[loc, loc + scale)`.

**Important:** Unlike a typical `uniform(min, max)` interface, scipy uses `loc` and `scale` where `scale` is the *width* of the distribution. To sample from `[min, max)`, set `loc = min` and `scale = max - min`.

**Example:** To sample from `[0.5, 1.5)`:

```yaml
- name: multiplier
  distribution: uniform
  loc: 0.5
  scale: 1.0  # 1.5 - 0.5 = 1.0
```

## scipy.stats Distributions

Continuous and discrete distributions from `scipy.stats` can be used by name (`rv_continuous` and `rv_discrete` instances). Arguments are passed directly to the distribution's `rvs()` method.

**Note:** This excludes some scipy.stats objects like `multivariate_normal` which are not `rv_continuous` or `rv_discrete` instances.

### Common Examples

**Normal distribution:**

```yaml
- name: offset
  distribution: norm
  loc: 0      # mean
  scale: 10   # standard deviation
```

**Beta distribution:**

```yaml
- name: probability
  distribution: beta
  a: 2
  b: 5
```

**Exponential distribution:**

```yaml
- name: wait_time
  distribution: expon
  scale: 5  # mean (1/lambda)
```

**Truncated normal (bounded):**

```yaml
- name: bounded_value
  distribution: truncnorm
  a: -2       # lower bound (in standard deviations)
  b: 2        # upper bound (in standard deviations)
  loc: 100    # mean
  scale: 10   # standard deviation
```

### Finding Distributions

See the [scipy.stats documentation](https://docs.scipy.org/doc/scipy/reference/stats.html) for the full list of available distributions and their parameters.

## Type Summary

| Distribution | Output Type | Range |
|-------------|-------------|-------|
| `constant` | any | fixed value |
| `choice` | any | from provided list |
| `randint` | int | `[low, high)` |
| `uniform` | float | `[loc, loc + scale)` |
| scipy.stats | varies | distribution-dependent |
