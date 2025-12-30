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

## Distribution Mode

By default, parameters are sampled once and injected as fixed values into your script. However, you can set `mode: distribution` to receive a distribution object instead, allowing you to sample multiple values within your script.

### Basic Usage

Add `mode: distribution` to any parameter definition:

```yaml
- name: x_dist
  distribution: uniform
  loc: 0
  scale: 100
  mode: distribution
```

The parameter `x_dist` will be a distribution object with a `.rvs()` method for sampling:

```python
# Sample a single value
value = x_dist.rvs()

# Sample multiple values
values = [x_dist.rvs() for _ in range(10)]

# Sample an array of values
array = x_dist.rvs(size=5)
```

### Reproducibility

Distribution objects maintain the random seed provided to the CLI, ensuring reproducible results:

```bash
# These will produce identical outputs
gen-art sample script.py -s 42
gen-art sample script.py -s 42
```

Within your script, multiple calls to `.rvs()` produce the same sequence with the same seed:

```python
# With seed 42, these values will always be the same
val1 = x_dist.rvs()
val2 = x_dist.rvs()
val3 = x_dist.rvs()
```

### Supported Distributions

All distribution types support distribution mode:

**Constant distributions:**
```yaml
- name: base_size
  distribution: constant
  value: 10
  mode: distribution
```
```python
# Always returns 10
size = base_size.rvs()
sizes = base_size.rvs(size=3)  # [10, 10, 10]
```

**Choice distributions:**
```yaml
- name: colour_dist
  distribution: choice
  values: ["red", "green", "blue"]
  weights: [0.5, 0.3, 0.2]
  mode: distribution
```
```python
# Sample colours multiple times
colours = [colour_dist.rvs() for _ in range(100)]
```

**Scipy distributions:**
```yaml
- name: radius_dist
  distribution: norm
  loc: 50
  scale: 10
  mode: distribution
```
```python
# Sample radii for multiple circles
radii = [radius_dist.rvs() for _ in range(num_circles)]
```

### Mixed Mode Example

You can mix sample and distribution modes in the same parameter space:

```yaml
parameters:
  - name: width
    distribution: constant
    value: 800
    mode: sample        # width is a fixed integer

  - name: radius_dist
    distribution: uniform
    loc: 10
    scale: 40
    mode: distribution  # radius_dist is a distribution object

  - name: num_circles
    distribution: randint
    low: 50
    high: 100
    mode: sample        # num_circles is a sampled integer
```

```python
from PIL import Image, ImageDraw
import random

img = Image.new("RGB", (width, width), "white")
draw = ImageDraw.Draw(img)

# Sample different radius for each circle
for _ in range(num_circles):
    x = random.randint(0, width)
    y = random.randint(0, width)
    r = int(radius_dist.rvs())  # Different radius each time
    draw.ellipse([x - r, y - r, x + r, y + r], fill="black")

img
```

### When to Use Distribution Mode

**Use `mode: sample` (default) when:**
- You want a single value for the entire image
- The parameter represents a global property (size, background colour, seed)

**Use `mode: distribution` when:**
- You need multiple different values in one image
- Each element should have variation (different sizes, colours, positions)
- You want to maintain reproducibility whilst sampling many values

## Type Summary

| Distribution | Output Type | Range |
|-------------|-------------|-------|
| `constant` | any | fixed value |
| `choice` | any | from provided list |
| `randint` | int | `[low, high)` |
| `uniform` | float | `[loc, loc + scale)` |
| scipy.stats | varies | distribution-dependent |
