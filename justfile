# Run `just` to list recipes.
default:
    @just --list

# Serve the site locally with live reload (http://localhost:8000)
serve:
    @uv run zensical serve

# Alias for serve
run: serve

# Build static HTML into site/
build:
    @uv run zensical build

# Check lesson structure, links and the sidebar
check:
    uv run tools/check_course.py

# Run the checker's own tests
test:
    uv run python -m unittest discover -s tools/tests

# Run the checker, its tests, then a full build
ci: check test build

# Delete build output (site/)
clean:
    @rm -rf site
