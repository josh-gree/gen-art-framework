# gen-art-framework

A Python framework for generating art from parameterised scripts. Define parameter distributions in YAML, and the framework samples from them to create unique variations of your artwork.

## Installation

```bash
pip install gen-art-framework
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add gen-art-framework
```

## Quick Start

Create a script with a YAML parameter block in its docstring:

```python
"""
parameters:
  - name: seed
    distribution: constant
    value: 42
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
  - name: colour
    distribution: choice
    values: ["#e94560", "#f39c12", "#00b894"]
"""

from PIL import Image, ImageDraw
import random

random.seed(seed)

img = Image.new("RGB", (width, height), "#1a1a2e")
draw = ImageDraw.Draw(img)

for _ in range(num_circles):
    x = random.randint(0, width)
    y = random.randint(0, height)
    r = random.randint(10, 50)
    draw.ellipse([x - r, y - r, x + r, y + r], fill=colour)

img
```

Generate images using the CLI:

```bash
# Generate a single image
gen-art sample my_script.py

# Generate 10 variations
gen-art sample my_script.py --count 10

# Specify output directory and seed for reproducibility
gen-art sample my_script.py -n 5 -o ./output -s 42
```

Output files are named `{script_name}_{index}_{seed}.png`.

## Documentation

- [CLI Usage](docs/cli.md) - Command-line interface reference
- [Writing Scripts](docs/writing-scripts.md) - How to write parameterised art scripts
- [Distributions](docs/distributions.md) - Available parameter distributions
- [Python API](docs/api.md) - Programmatic usage
- [Examples](docs/examples.md) - Walkthrough of example scripts
