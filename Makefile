#SHELL := /bin/bash

#DATA_PATH = $(shell pwd)
#VERSION ?= $(shell git describe --tags --always --dirty)

#ifneq (,$(wildcard ./deployment/.env))
#    include deployment/.env
#    export
#	ENV_FILE_PARAM=deployment/.env
#endif

# default target is help
#.DEFAULT_GOAL := help

#help: ## Displays this help message
#	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Deployment

PROJDIR := $(realpath $(CURDIR))
#BUILDDIR := $(PROJDIR)/deployment

.PHONY: format-all
format-all:
	@echo Sorting imports ...
	@isort --settings-path=./backend/pyproject.toml --py 312 --virtual-env .venv ./backend/.
	@echo Reformatting with Ruff ...
	@ruff --config ./backend/pyproject.toml format ./backend/.
	@echo Running Flake8 ...
	@flake8 ./backend --config=./backend/pyproject.toml
	@echo Finished :\)

.PHONY: security-all
security-all:
	@bandit -c ./backend/pyproject.toml -r ./backend/.
	@semgrep --config p/ci --include='*.py' --exclude='test_*.py'cd ..


.PHONY: up-dev
up-dev:
	@echo "Starting development environment..."
	@make -C ./deployment up-dev
	@echo "Development environment started"

.PHONY: down-dev
down-dev:
	@echo "Stopping development environment..."
	@make -C ./deployment down-dev
	@echo "Development environment stopped"

.PHONY: down-dev-volumes
down-dev-volumes:
	@echo "Stopping development+VOLUMES environment..."
	@make -C ./deployment down-dev-volumes
	@echo "Development+VOLUMES environment stopped"

.PHONY: up-backend
up-backend:
	@echo "Starting backend environment..."
	@make -C ./deployment up-backend
	@echo "Backend environment started"

.PHONY: up-db
up-db:
	@echo "Starting DB environment..."
	@make -C ./deployment up-db
	@echo "DB environment started"

# Set PROJDIR to the absolute path of the project root using pwd
PROJDIR := $(shell pwd)

.PHONY: test-local
test-local: ## Run pytest tests locally in the virtual environment
	@echo "Running pytest tests locally..."
	@if [ ! -f "$(PROJDIR)/venv/bin/activate" ]; then \
		echo "Error: Virtual environment not found at $(PROJDIR)/venv/bin/activate"; \
		exit 1; \
	fi
	@source $(PROJDIR)/venv/bin/activate && \
		pytest $(PROJDIR)/backend/api/tests/routers -v $(PYTEST_ARGS)
	@echo "Local pytest tests completed"

.PHONY: test-docker
test-docker:
	@make -C ./deployment test-docker