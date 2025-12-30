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

## Releases

Use the `just release` command to create new releases:

```bash
just release <major|minor|patch> "Release message"
```

- **patch**: Bug fixes and small improvements (0.2.0 → 0.2.1)
- **minor**: New features, backwards compatible (0.2.0 → 0.3.0)
- **major**: Breaking changes (0.2.0 → 1.0.0)

The command will:
1. Verify you're on main with a clean, up-to-date working tree
2. Calculate the new version based on the latest tag
3. Create and push a git tag
4. Trigger the CI workflow to publish to PyPI

## Code Style

- Keep imports at module level unless there's a meaningful reason not to (e.g. circular imports, optional dependencies)
