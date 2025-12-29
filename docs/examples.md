# Example Scripts

This document walks through example scripts to illustrate how to write parameterised generative art.

## circles.py - Simple Example

A basic script that draws random circles on a canvas.

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

### Parameter Breakdown

| Parameter | Distribution | Purpose |
|-----------|-------------|---------|
| `width`, `height` | `constant` | Fixed canvas dimensions |
| `num_circles` | `randint` | Varies density between samples |
| `seed` | `randint` | Makes internal randomness reproducible |
| `background` | `choice` | Dark colour palette options |
| `colour` | `choice` | Bright accent colours |

### Key Techniques

**Fixed dimensions with `constant`:** Using constant values for width and height ensures consistent image sizes across all samples.

**Internal seed for reproducibility:** The `seed` parameter is passed to `random.seed()`, making the circle positions deterministic for each sample. Given the same parameters, the script produces identical output.

**Colour choices:** Using `choice` for colours creates cohesive palettes while still varying between samples.

---

## flow_field.py - Advanced Example

A more complex script that creates flow field visualisations using pseudo-noise.

```python
"""
parameters:
  - name: width
    distribution: constant
    value: 1000
  - name: height
    distribution: constant
    value: 800
  - name: seed
    distribution: randint
    low: 0
    high: 100000
  - name: background
    distribution: choice
    values: ["#0d1117", "#1a1a2e", "#2d132c", "#0a192f"]
  - name: line_colour
    distribution: choice
    values: ["#00d4ff", "#ff6b6b", "#c9f364", "#f8b500", "#7c3aed", "#06ffa5"]
  - name: num_lines
    distribution: randint
    low: 400
    high: 900
  - name: line_length
    distribution: randint
    low: 80
    high: 200
  - name: line_width
    distribution: randint
    low: 1
    high: 3
  - name: line_alpha
    distribution: uniform
    loc: 0.3
    scale: 0.5
  - name: noise_scale
    distribution: uniform
    loc: 0.003
    scale: 0.012
  - name: noise_offset
    distribution: uniform
    loc: 0
    scale: 100
  - name: turbulence
    distribution: uniform
    loc: 0.8
    scale: 1.5
  - name: step_size
    distribution: uniform
    loc: 2
    scale: 4
"""

from PIL import Image, ImageDraw
import math
import random

random.seed(seed)

img = Image.new("RGBA", (width, height), background)
draw = ImageDraw.Draw(img)


def noise_angle(x, y, scale, offset):
    """Simple pseudo-noise for angle calculation."""
    nx = x * scale + offset
    ny = y * scale + offset
    return (
        math.sin(nx * 1.5) * math.cos(ny * 1.5) +
        math.sin(nx * 0.7 + ny * 0.5) * 0.5 +
        math.cos(nx * 0.3 - ny * 0.8) * 0.3
    ) * math.pi * turbulence


def draw_flow_line(start_x, start_y):
    """Draw a single flow line from a starting point."""
    x, y = start_x, start_y
    points = [(x, y)]

    for _ in range(line_length):
        angle = noise_angle(x, y, noise_scale, noise_offset)
        x += math.cos(angle) * step_size
        y += math.sin(angle) * step_size

        if x < 0 or x >= width or y < 0 or y >= height:
            break
        points.append((x, y))

    if len(points) > 1:
        for i in range(len(points) - 1):
            progress = i / len(points)
            alpha = int(255 * (1 - progress) * line_alpha)
            colour_with_alpha = line_colour + f"{alpha:02x}"
            draw.line([points[i], points[i + 1]], fill=colour_with_alpha, width=line_width)


# Create a grid of starting points with some randomness
grid_size = int(math.sqrt(num_lines))
spacing_x = width / grid_size
spacing_y = height / grid_size

for i in range(grid_size):
    for j in range(grid_size):
        x = i * spacing_x + random.uniform(-spacing_x * 0.3, spacing_x * 0.3)
        y = j * spacing_y + random.uniform(-spacing_y * 0.3, spacing_y * 0.3)
        draw_flow_line(x, y)

img
```

### Parameter Breakdown

| Parameter | Distribution | Purpose |
|-----------|-------------|---------|
| `width`, `height` | `constant` | Fixed canvas size |
| `seed` | `randint` | Internal randomness seed |
| `background`, `line_colour` | `choice` | Colour palette |
| `num_lines` | `randint` | Density of the flow field |
| `line_length` | `randint` | How far lines travel |
| `line_width` | `randint` | Stroke thickness |
| `line_alpha` | `uniform` | Transparency variation |
| `noise_scale` | `uniform` | Scale of the noise pattern |
| `noise_offset` | `uniform` | Shifts the noise pattern |
| `turbulence` | `uniform` | Intensity of angle changes |
| `step_size` | `uniform` | Distance per step |

### Key Techniques

**Using `uniform` for continuous parameters:** Flow fields benefit from continuous variation. Using `uniform` for `noise_scale`, `turbulence`, and `step_size` creates smooth variation between samples.

**Derived behaviour:** The `num_lines` parameter indirectly controls density through the grid calculation. Fewer lines means more spacing, creating different visual densities.

**RGBA for transparency:** Using `"RGBA"` mode allows alpha blending, creating depth where lines overlap.

**Noise parameters:** `noise_scale` controls the "zoom" of the pattern, `noise_offset` shifts it, and `turbulence` controls how much the lines curve. Together they create unique flow patterns.

---

## Design Principles

When writing your own scripts:

1. **Use `constant` for structural parameters** - Canvas size, fixed ratios
2. **Use `choice` for categorical variety** - Colours, styles, modes
3. **Use `randint` for discrete quantities** - Counts, sizes, positions
4. **Use `uniform` for continuous values** - Opacity, scale factors, angles
5. **Include a `seed` parameter** - For reproducible internal randomness
6. **Keep palettes cohesive** - Limit choices to colours that work together
7. **Balance variation** - Too many varying parameters can create chaos; anchor some values
