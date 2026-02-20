PYTHON_CMD  := uv run python3 main.py maps/challenger/01_the_impossible_dream.txt --visual

BOLD   := \033[1m
RESET  := \033[0m
GREEN  := \033[32m

.PHONY: all install run debug clean lint lint-strict

all: install run

install:
	@echo "$(BOLD)🚀 Initializing project environment and syncing dependencies...$(RESET)"
	@pip install uv
	@uv sync
	@echo "\n$(BOLD)$(GREEN)✅ Environment setup complete.$(RESET)"

run:
	@echo "$(BOLD)🕹️  Executing main script...$(RESET)"
	$(PYTHON_CMD)

debug:
	@echo "$(BOLD)⚙️ Executing main script with pdb...$(RESET)"
	$(PYTHON_CMD) -m pdb

clean:
	@echo "$(BOLD)🗑️  Cleaning up build artifacts and cache...$(RESET)"
	rm -rf .mypy_cache srcs/visualizer/__pycache__ srcs/parsing/__pycache__ srcs/__pycache__ srcs/solver/__pycache__ srcs/managing/__pycache__
	@echo "\n$(BOLD)$(GREEN)🧹 Workspace is clean.$(RESET)"

lint:
	@echo "$(BOLD)🔎 Running static code analysis (src only + silent imports)...$(RESET)"
	flake8 --exclude=.venv,llm_sdk/__init__.py
	mypy srcs --follow-imports=silent --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@echo "$(BOLD)🔎 Running static code analysis (strict option)...$(RESET)"
	flake8 --exclude=.venv
	mypy src --follow-imports=silent --strict
