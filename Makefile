MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs
MYPY_STRICT = --strict
FLAKE_STRICT = --max-complexity=30

MAIN = src/__main__.py
CONFIG = config.json

.PHONY: all install run clean lint lint-strict debug build

all: run

install:
	@uv sync

run:
	@uv run python -m src $(CONFIG)

clean:
	@rm -Rf .venv
	@rm -Rf __pycache__
	@rm -Rf src/__pycache__
	@rm -Rf .mypy_cache
	@rm -Rf uv.lock
	@echo "All code clean"

clean-package:
	@rm -rf build
	@rm -rf dist
	@rm Pacman-42.spec
	@echo "The package is deleted."

lint:
	@uv run python3 -m mypy --exclude 'llm_sdk' $(MYPY_FLAGS) .
	@uv run python3 -m flake8 --exclude .venv,llm_sdk .

lint-strict:
	@uv run python3 -m mypy --exclude 'llm_sdk' $(MYPY_FLAGS) $(MYPY_STRICT) .
	@uv run python3 -m flake8 --exclude .venv,llm_sdk $(FLAKE_STRICT) .

debug:
	@uv run python3 -m pdb $(MAIN)

build:
	@bash build.sh