# Writing Scripts

Scripts are Python files that define parameter distributions in a YAML docstring. The framework samples from these distributions and injects the values as global variables before executing your code.

## Basic Structure

A script has two parts:

1. A module docstring containing YAML parameter definitions
2. Python code that uses those parameters and produces a PIL Image

```python
"""
parameters:
  - name: width
    distribution: constant
    value: 800
  - name: colour
    distribution: choice
    values: ["red", "blue", "green"]
"""

from PIL import Image

img = Image.new("RGB", (width, width), colour)

img  # Final expression must be a PIL Image
```

## YAML Format

The docstring must start with `parameters:` and contain a list of parameter definitions:

```yaml
parameters:
  - name: param_name
    distribution: distribution_type
    # additional arguments depend on distribution type
```

Each parameter requires:

- `name` - Variable name (will be available as a global in your script)
- `distribution` - Type of distribution to sample from

Additional fields depend on the distribution type. See [Distributions](distributions.md) for details.

## Parameter Injection

Parameters are injected as Python globals before your script runs. They're available immediately without any imports:

```python
"""
parameters:
  - name: size
    distribution: randint
    low: 100
    high: 500
  - name: bg_colour
    distribution: constant
    value: "#ffffff"
"""

# 'size' and 'bg_colour' are already defined
print(f"Creating {size}x{size} image with {bg_colour} background")
```

## Final Expression

The last line of your script must be an expression that evaluates to a `PIL.Image.Image`. This is the image that will be saved.

**Correct:**

```python
img = Image.new("RGB", (100, 100))
# ... drawing code ...
img  # Bare variable name as final expression
```

**Incorrect:**

```python
img = Image.new("RGB", (100, 100))
# ... drawing code ...
img.save("output.png")  # save() returns None, not the image
```

**Also incorrect:**

```python
img = Image.new("RGB", (100, 100))
# ... drawing code ...
# No final expression - the framework won't know what to save
```

## Reserved Parameter Names

Parameter names cannot shadow Python builtins or keywords. The following names are reserved and will raise an error:

- Python keywords: `if`, `for`, `while`, `class`, `def`, `return`, `import`, etc.
- Python builtins: `print`, `len`, `range`, `list`, `dict`, `str`, `int`, etc.

## Working with Randomness

For internal randomness (beyond parameter sampling), use Python's `random` module with a seed parameter:

```python
"""
parameters:
  - name: seed
    distribution: randint
    low: 0
    high: 100000
  - name: num_shapes
    distribution: randint
    low: 10
    high: 50
"""

import random
random.seed(seed)

# Now random calls are reproducible for each sample
for _ in range(num_shapes):
    x = random.randint(0, 800)
    # ...
```

This ensures that given the same parameter values, your script produces identical output.

## Complete Example

```python
"""
parameters:
  - name: width
    distribution: constant
    value: 800
  - name: height
    distribution: constant
    value: 600
  - name: num_circles
    distribution: randint
    low: 20
    high: 50
  - name: seed
    distribution: randint
    low: 0
    high: 10000
  - name: background
    distribution: choice
    values: ["#1a1a2e", "#16213e", "#0f3460"]
  - name: colour
    distribution: choice
    values: ["#e94560", "#f39c12", "#00b894", "#6c5ce7"]
"""

from PIL import Image, ImageDraw
import random

random.seed(seed)

img = Image.new("RGB", (width, height), background)
draw = ImageDraw.Draw(img)

for _ in range(num_circles):
    x = random.randint(0, width)
    y = random.randint(0, height)
    r = random.randint(10, 50)
    draw.ellipse([x - r, y - r, x + r, y + r], fill=colour)

img
```
