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
    mode: distribution
  - name: num_lines
    distribution: randint
    low: 400
    high: 900
  - name: line_length
    distribution: randint
    low: 80
    high: 200
    mode: distribution
  - name: line_width
    distribution: randint
    low: 1
    high: 3
    mode: distribution
  - name: line_alpha
    distribution: uniform
    loc: 0.3
    scale: 0.5
    mode: distribution
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
    nx = x * scale + offset
    ny = y * scale + offset
    return (
        math.sin(nx * 1.5) * math.cos(ny * 1.5) +
        math.sin(nx * 0.7 + ny * 0.5) * 0.5 +
        math.cos(nx * 0.3 - ny * 0.8) * 0.3
    ) * math.pi * turbulence


def draw_flow_line(start_x, start_y):
    x, y = start_x, start_y
    points = [(x, y)]

    # Sample line properties for this line
    length = int(line_length.rvs())
    lwidth = int(line_width.rvs())
    alpha_mult = line_alpha.rvs()
    colour = line_colour.rvs()

    for _ in range(length):
        angle = noise_angle(x, y, noise_scale, noise_offset)
        x += math.cos(angle) * step_size
        y += math.sin(angle) * step_size

        if x < 0 or x >= width or y < 0 or y >= height:
            break
        points.append((x, y))

    if len(points) > 1:
        for i in range(len(points) - 1):
            progress = i / len(points)
            alpha = int(255 * (1 - progress) * alpha_mult)
            colour_with_alpha = colour + f"{alpha:02x}"
            draw.line([points[i], points[i + 1]], fill=colour_with_alpha, width=lwidth)


grid_size = int(math.sqrt(num_lines))
spacing_x = width / grid_size
spacing_y = height / grid_size

for i in range(grid_size):
    for j in range(grid_size):
        x = i * spacing_x + random.uniform(-spacing_x * 0.3, spacing_x * 0.3)
        y = j * spacing_y + random.uniform(-spacing_y * 0.3, spacing_y * 0.3)
        draw_flow_line(x, y)

img
