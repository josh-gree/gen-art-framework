"""Command-line interface for gen-art-framework."""

import ast
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
