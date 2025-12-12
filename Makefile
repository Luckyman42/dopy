# Build
build:
	uv build

# Run linter
linter:
	uv run ruff check dopy

# Run linter
linter-fix:
	uv run ruff check dopy --fix

# Run static type checker
type-checker:
	uv run pyright 

# Run formatter
formatter:
	uv run ruff format dopy

# Formatter + Linter + type-checker
lint-all: formatter linter type-checker

# Run tests
test: 
	uv run pytest -q

coverage:
	uv run pytest --cov=dopy --cov-report=term-missing

# Install dependencies for developing the project
install-dev-dependencies:
	pip install uv
	uv sync
	uv run pre-commit install
