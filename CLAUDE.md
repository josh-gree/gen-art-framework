# gen-art-framework

Python library using uv for dependency management.

## Commands

Run `just` to see available commands (test, lint, format, shell, jupyter).

## Project Structure

- `src/gen_art_framework/` - library source code
- `tests/` - test files
- `nbs/` - notebooks (tracked)
- `scratch/` - throwaway scripts and notebooks (gitignored)

## Dependencies

- Add runtime deps: `uv add <package>`
- Add dev deps: `uv add --dev <package>`
- Run anything: `uv run <command>`

## Code Style

- Keep imports at module level unless there's a meaningful reason not to (e.g. circular imports, optional dependencies)
