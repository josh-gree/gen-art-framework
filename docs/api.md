# Python API

For programmatic usage, the framework exports functions and data classes that let you parse parameters, sample values, and execute scripts.

## Public Exports

```python
from gen_art_framework import (
    execute_script,
    parse_parameter_space,
    sample_parameter_space,
    ParameterDefinition,
    ParameterSpace,
)
```

## Functions

### `parse_parameter_space(docstring: str) -> ParameterSpace`

Parse a YAML docstring into a `ParameterSpace` object.

```python
from gen_art_framework import parse_parameter_space

docstring = """
parameters:
  - name: width
    distribution: constant
    value: 800
  - name: count
    distribution: randint
    low: 5
    high: 20
"""

space = parse_parameter_space(docstring)
print(len(space))  # 2
print(space["width"].distribution)  # "constant"
```

**Raises:**

- `ValueError` - If the YAML is malformed, missing required fields, contains reserved parameter names, or has duplicate parameter names

### `sample_parameter_space(space: ParameterSpace, rng: np.random.Generator) -> dict[str, Any]`

Sample concrete values from a parameter space.

```python
import numpy as np
from gen_art_framework import parse_parameter_space, sample_parameter_space

space = parse_parameter_space(docstring)
rng = np.random.default_rng(42)

params = sample_parameter_space(space, rng)
# {'width': 800, 'count': 14}
```

**Arguments:**

- `space` - A `ParameterSpace` object
- `rng` - A numpy random generator for reproducible sampling

**Returns:**

A dictionary mapping parameter names to sampled values.

**Raises:**

- `ValueError` - If the distribution type is unknown, or if distribution arguments are invalid (e.g., missing `value` for `constant`, weights that don't sum to 1.0 for `choice`)

### `execute_script(script_path: Path | str, parameters: dict[str, Any]) -> Image.Image`

Execute a script with parameters injected as globals.

```python
from pathlib import Path
from gen_art_framework import execute_script

params = {"width": 800, "height": 600, "colour": "#ff0000"}
image = execute_script(Path("my_script.py"), params)
image.save("output.png")
```

**Arguments:**

- `script_path` - Path to the Python script
- `parameters` - Dictionary of parameter values to inject

**Returns:**

The PIL Image produced by the script.

**Raises:**

- `ValueError` - If the script doesn't exist, has syntax errors, doesn't produce a PIL Image, or execution fails

**Security note:** Scripts are executed with `exec()` and have full system access. Only run scripts you trust.

## Data Classes

### `ParameterDefinition`

A single parameter definition.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ParameterDefinition:
    name: str              # Parameter name
    distribution: str      # Distribution type
    args: dict[str, Any]   # Distribution arguments
```

### `ParameterSpace`

Container for multiple parameter definitions. Supports iteration and lookup by name.

```python
from dataclasses import dataclass

@dataclass
class ParameterSpace:
    parameters: list[ParameterDefinition]
```

**Usage:**

```python
space = parse_parameter_space(docstring)

# Iteration
for param in space:
    print(param.name, param.distribution)

# Length
print(len(space))  # Number of parameters

# Lookup by name (raises KeyError if parameter doesn't exist)
width_param = space["width"]
print(width_param.args)  # {"value": 800}
```

## Complete Example

Generate multiple images programmatically:

```python
import ast
from pathlib import Path
import numpy as np
from gen_art_framework import (
    parse_parameter_space,
    sample_parameter_space,
    execute_script,
)

# Read script and parse parameter space
script_path = Path("circles.py")
tree = ast.parse(script_path.read_text())
docstring = ast.get_docstring(tree)
space = parse_parameter_space(docstring)

# Generate 10 images with different seeds
rng = np.random.default_rng(42)
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

for i in range(10):
    # Sample parameters
    params = sample_parameter_space(space, rng)

    # Execute and save
    image = execute_script(script_path, params)
    image.save(output_dir / f"image_{i}.png")
```

## Custom Workflows

The API allows for workflows beyond simple sampling:

```python
# Fix some parameters, sample others
space = parse_parameter_space(docstring)

fixed_params = {"width": 1920, "height": 1080}
rng = np.random.default_rng()

for _ in range(5):
    params = sample_parameter_space(space, rng)
    params.update(fixed_params)  # Override with fixed values
    image = execute_script(script_path, params)
```

```python
# Generate a grid exploring two parameters
widths = [400, 800, 1200]
counts = [10, 25, 50]

for w in widths:
    for c in counts:
        params = {"width": w, "height": w, "count": c, "colour": "#ff0000"}
        image = execute_script(script_path, params)
        image.save(f"grid_{w}x{c}.png")
```
