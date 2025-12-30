"""Command-line interface for gen-art-framework."""

import ast
from importlib.resources import files
from pathlib import Path

import click
import numpy as np

from gen_art_framework.distributions import sample_parameter_space
from gen_art_framework.executor import execute_script
from gen_art_framework.schema import parse_parameter_space


@click.group()
def cli():
    """Gen-art-framework: Generate art from parameterised scripts."""
    pass


@cli.command()
@click.argument("script", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--count",
    "-n",
    default=1,
    type=click.IntRange(min=1),
    help="Number of images to generate.",
)
@click.option(
    "--output",
    "-o",
    default=".",
    type=click.Path(path_type=Path),
    help="Output directory for generated images.",
)
@click.option(
    "--seed",
    "-s",
    default=None,
    type=int,
    help="Random seed for reproducibility.",
)
def sample(script: Path, count: int, output: Path, seed: int | None):
    """Generate images by sampling parameter space from a script.

    SCRIPT is a Python file with a YAML parameter space in its docstring.
    """
    # Read script and extract docstring
    script_content = script.read_text()

    # Extract docstring from script
    try:
        docstring = _extract_docstring(script_content)
    except SyntaxError as e:
        raise click.ClickException(
            f"Script '{script}' has a syntax error: {e.msg} (line {e.lineno})"
        ) from e
    if docstring is None:
        raise click.ClickException(
            f"Script '{script}' has no docstring with parameter space."
        )

    # Parse parameter space from docstring
    try:
        param_space = parse_parameter_space(docstring)
    except ValueError as e:
        raise click.ClickException(f"Failed to parse parameter space: {e}") from e

    # Create output directory if needed
    output.mkdir(parents=True, exist_ok=True)

    # Set up random generator
    if seed is None:
        seed = int(np.random.default_rng().integers(0, 2**31))
        click.echo(f"Using random seed: {seed}", err=True)

    rng = np.random.default_rng(seed)

    # Get script name without extension for filenames
    script_name = script.stem

    # Generate images
    for i in range(count):
        # Get a seed for this specific sample (for filename and reproducibility)
        sample_seed = rng.integers(0, 2**31)
        sample_rng = np.random.default_rng(sample_seed)

        # Sample parameters
        params = sample_parameter_space(param_space, sample_rng)

        click.echo(f"Generating image {i + 1}/{count}...", err=True)

        # Execute script
        try:
            image = execute_script(script, params)
        except ValueError as e:
            raise click.ClickException(f"Script execution failed: {e}") from e

        # Save image
        filename = f"{script_name}_{i}_{sample_seed}.png"
        image_path = output / filename
        image.save(image_path)

        click.echo(f"  Saved: {image_path}", err=True)

    click.echo(f"Generated {count} image(s) in {output}", err=True)


@cli.command()
@click.argument("example", type=str)
@click.option(
    "--output",
    "-o",
    default=".",
    type=click.Path(path_type=Path),
    help="Output directory for example files.",
)
def install_example(example: str, output: Path):
    """Install example scripts to your filesystem.

    EXAMPLE is the name of an example to install, or "all" to install all examples.

    Available examples: circles, flow_field
    """
    # Get available examples
    examples_dict = _discover_examples()

    if not examples_dict:
        raise click.ClickException("No examples found in the package.")

    # Determine which examples to install
    if example == "all":
        examples_to_install = examples_dict
    elif example in examples_dict:
        examples_to_install = {example: examples_dict[example]}
    else:
        available = ", ".join(sorted(examples_dict.keys()))
        raise click.ClickException(
            f"Unknown example '{example}'. Available examples: {available}"
        )

    # Create output directory if needed
    output.mkdir(parents=True, exist_ok=True)

    # Copy examples
    for name, content in examples_to_install.items():
        target_path = output / f"{name}.py"

        # Check if file exists
        if target_path.exists():
            click.echo(f"Skipping {name}.py (already exists)", err=True)
            continue

        # Write file
        target_path.write_text(content)
        click.echo(f"Installed: {target_path}", err=True)

    installed_count = len(examples_to_install)
    click.echo(f"Installed {installed_count} example(s) to {output}", err=True)


def _discover_examples() -> dict[str, str]:
    """Discover available example scripts from the installed package.

    Returns:
        Dictionary mapping example names to their file contents.
    """
    examples = {}

    try:
        examples_path = files("gen_art_framework.examples")

        for item in examples_path.iterdir():
            if item.name.endswith(".py") and item.name != "__init__.py":
                example_name = item.name[:-3]  # Remove .py extension
                content = item.read_text()
                examples[example_name] = content
    except (AttributeError, FileNotFoundError):
        pass

    return examples


def _extract_docstring(script_content: str) -> str | None:
    """Extract the module docstring from script content.

    Raises:
        SyntaxError: If the script contains invalid Python syntax.
    """
    tree = ast.parse(script_content)
    return ast.get_docstring(tree)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
