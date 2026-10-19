MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs
MYPY_STRICT = --strict
FLAKE_STRICT = --max-complexity=25

MAIN = src/__main__.py
CONFIG = config.json

.PHONY: all install run clean lint lint-strict debug

all: run

install:
	@uv sync

run:
	@uv run python -m src $(CONFIG)

clean:
	@rm -rf .venv __pycache__ .mypy_cache
	@find src -type d -name '__pycache__' -prune -exec rm -rf {} +
	@rm -Rf uv.lock
	@rm -Rf .venv
	@echo "All caches cleaned"

lint:
	@uv run python3 -m mypy --exclude 'llm_sdk' $(MYPY_FLAGS) .
	@uv run python3 -m flake8 --exclude .venv,llm_sdk .

lint-strict:
	@uv run python3 -m mypy --exclude 'llm_sdk' $(MYPY_FLAGS) $(MYPY_STRICT) .
	@uv run python3 -m flake8 --exclude .venv,llm_sdk $(FLAKE_STRICT) .

debug:
	@uv run python3 -m pdb $(MAIN)
