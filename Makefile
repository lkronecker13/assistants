# Makefile

# Define the default target
.DEFAULT_GOAL := help

# Define phony targets
.PHONY: install help

set-up-project: ## Set up tools and dependencies
	poetry run pip install --upgrade pip
	poetry run pip install pre-commit
	chmod +x .git/hooks/pre-commit

install: ## Make sure you are using a local version of python >= 3.10 and < 3.11
	poetry install

update: ## Update .lock file with new dependencies.
	poetry update

lint:  ## Check for code issues.
	poetry run ruff check .

lint-fix:  ## Check and fix code issues.
	poetry run ruff check --fix .

format:  ## Format code
	poetry run ruff format .

assistant-local-run:
	poetry run chainlit run assistants/main.py

assistant-service-build:
	DOCKER_BUILDKIT=1 docker build --target=runtime . -t assistant:latest

assistant-service-start: #ollama-start
	docker-compose up assistant
	#docker run --network host -d --name assistant -p 8000:8000 assistant:latest

help: ## Display this help message
	@echo "Usage: make [target]"
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)