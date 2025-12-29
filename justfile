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
