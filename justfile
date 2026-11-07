# Run `just` to list recipes.
default:
    @just --list

# Serve the site locally with live reload (http://localhost:8000)
serve:
    @uv run zensical serve --open

# Alias for serve
run: serve

# Build static HTML into site/
build:
    @uv run zensical build

# Build the site, then open the built copy in the default browser
open: build
    @uv run python -c "import pathlib, webbrowser; webbrowser.open(pathlib.Path('site/index.html').resolve().as_uri())"

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
