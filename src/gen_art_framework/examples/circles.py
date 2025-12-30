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
    mode: distribution
  - name: radius
    distribution: randint
    low: 10
    high: 50
    mode: distribution
"""

from PIL import Image, ImageDraw
import random

random.seed(seed)

img = Image.new("RGB", (width, height), background)
draw = ImageDraw.Draw(img)

for _ in range(num_circles):
    x = random.randint(0, width)
    y = random.randint(0, height)
    r = int(radius.rvs())
    c = colour.rvs()
    draw.ellipse([x - r, y - r, x + r, y + r], fill=c)

img
