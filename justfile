# List available commands
default:
    @just --list

# Run tests
test *args:
    uv run pytest {{args}}

# Run tests with coverage
test-cov:
    uv run pytest --cov

# Format code
fmt:
    uv run ruff format .

# Lint code
lint:
    uv run ruff check .

# Lint and fix
lint-fix:
    uv run ruff check . --fix

# Format and lint
check: fmt lint

# Start IPython shell with autoreload
shell:
    uv run ipython -i -c "get_ipython().run_line_magic('load_ext', 'autoreload'); get_ipython().run_line_magic('autoreload', '2')"

# Start Jupyter Lab
jupyter:
    uv run jupyter lab

# Build package
build:
    rm -rf dist/
    uv build

# Bump version (patch, minor, or major)
bump level:
    #!/usr/bin/env python3
    import re
    from pathlib import Path

    level = "{{level}}"
    if level not in ("patch", "minor", "major"):
        raise SystemExit(f"Invalid level: {level}. Must be patch, minor, or major")

    pyproject = Path("pyproject.toml")
    content = pyproject.read_text()

    match = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
    if not match:
        raise SystemExit("Could not find version in pyproject.toml")

    major, minor, patch = map(int, match.groups())

    if level == "major":
        major, minor, patch = major + 1, 0, 0
    elif level == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    new_content = re.sub(r'version = "\d+\.\d+\.\d+"', f'version = "{new_version}"', content)
    pyproject.write_text(new_content)
    print(f"Bumped version to {new_version}")

# Publish to PyPI
publish: build
    uv run twine upload dist/*
