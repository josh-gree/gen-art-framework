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

# Release a new version (bump: major|minor|patch, message: release message)
release bump message:
    #!/usr/bin/env bash
    set -euo pipefail

    # Environment verification
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [ "$BRANCH" != "main" ]; then
        echo "Error: Must be on main branch (currently on $BRANCH)"
        exit 1
    fi

    if [ -n "$(git status --porcelain)" ]; then
        echo "Error: Working tree has uncommitted changes"
        exit 1
    fi

    git fetch origin
    BEHIND=$(git rev-list HEAD...origin/main --count)
    if [ "$BEHIND" -gt 0 ]; then
        echo "Error: Branch is $BEHIND commit(s) behind origin/main"
        exit 1
    fi

    # Version calculation
    LATEST_TAG=$(git describe --tags --abbrev=0 --match "v*" 2>/dev/null || echo "v0.0.0")
    VERSION=${LATEST_TAG#v}
    IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"

    case "{{bump}}" in
        major)
            MAJOR=$((MAJOR + 1))
            MINOR=0
            PATCH=0
            ;;
        minor)
            MINOR=$((MINOR + 1))
            PATCH=0
            ;;
        patch)
            PATCH=$((PATCH + 1))
            ;;
        *)
            echo "Error: bump must be major, minor, or patch"
            exit 1
            ;;
    esac

    NEW_VERSION="v$MAJOR.$MINOR.$PATCH"

    # Tag creation and push
    git tag -a "$NEW_VERSION" -m "{{message}}"
    git push origin "$NEW_VERSION"

    echo "Released $NEW_VERSION"
    REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
    echo "CI workflow: https://github.com/$REPO/actions"
