# CLI Usage

The `gen-art` command-line tool generates images by sampling from parameterised scripts.

## Commands

### `gen-art sample`

Generate images by sampling parameter space from a script.

```bash
gen-art sample SCRIPT [OPTIONS]
```

**Arguments:**

- `SCRIPT` - Path to a Python file with a YAML parameter space in its docstring

**Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--count` | `-n` | 1 | Number of images to generate |
| `--output` | `-o` | `.` | Output directory for generated images |
| `--seed` | `-s` | random | Random seed for reproducibility |

## Output Filenames

Generated images follow the naming pattern:

```
{script_name}_{index}_{seed}.png
```

- `script_name` - The name of the input script (without `.py`)
- `index` - Zero-based index of the image in the batch
- `seed` - The seed used for that specific sample

For example, running `gen-art sample circles.py -n 3` might produce:

```
circles_0_1847293847.png
circles_1_9283746192.png
circles_2_3847291028.png
```

## Reproducibility

Use the `--seed` option to generate reproducible results:

```bash
# These two commands produce identical images
gen-art sample my_script.py -n 5 -s 42
gen-art sample my_script.py -n 5 -s 42
```

When no seed is provided, a random seed is generated and printed to stderr:

```
$ gen-art sample circles.py
Using random seed: 1847293847
Generating image 1/1...
  Saved: ./circles_0_1847293847.png
Generated 1 image(s) in .
```

## Examples

```bash
# Generate a single image in the current directory
gen-art sample circles.py

# Generate 20 variations
gen-art sample circles.py --count 20

# Save to a specific directory
gen-art sample circles.py -n 10 -o ./gallery

# Reproducible batch generation
gen-art sample circles.py -n 5 --seed 12345
```
