#!/usr/bin/make -f
# -*- makefile -*-

SHELL         := /bin/bash
.SHELLFLAGS   := -eu -o pipefail -c
.DEFAULT_GOAL := help
.LOGGING      := 0

.ONESHELL:             ;	# Recipes execute in same shell
.NOTPARALLEL:          ;	# Wait for this target to finish
.SILENT:               ;	# No need for @
.EXPORT_ALL_VARIABLES: ;	# Export variables to child processes.
.DELETE_ON_ERROR:      ;	# Delete target if recipe fails.

# Modify the block character to be `-\t` instead of `\t`
ifeq ($(origin .RECIPEPREFIX), undefined)
	$(error This version of Make does not support .RECIPEPREFIX.)
endif
.RECIPEPREFIX = -


PROJECT_DIR := $(shell git rev-parse --show-toplevel)
SRC_DIR     := $(PROJECT_DIR)/src
BUILD_DIR   := $(PROJECT_DIR)/dist

default: $(.DEFAULT_GOAL)
all: help


.PHONY: help
help: ## List commands <default>
-	echo -e "USAGE: make \033[36m[COMMAND]\033[0m\n"
-	echo "Available commands:"
-	awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\t\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)


.PHONY: lint
lint: ## Lint the code
-	black $(PROJECT_DIR)
-	ruff check $(PROJECT_DIR) --fix


.PHONY: serve
serve: build ## Serve the site locally
-	@echo "Serving site at http://localhost:8000"
-	@echo "Press Ctrl+C to stop"
-	cd ./reports/ && python -m http.server 8000


.PHONY: install
install: ## Install dependencies (if needed)
-	pip install -e .


.PHONY: build
build: ## Build the database, HTML page, and chart page
-   benchci compat
-	benchci build-pages
-	benchci build-charts
-   benchci build-spider-chart

# .PHONY: build
# build: ## Build the application
# -	pip install wheel
# -	pip install --upgrade pip wheel
# -	pip install --editable ".[developer]"
# -	hatch build --clean --target wheel


.PHONY: clean
clean: ## Clean generated files
-	rm -f docs/database.json
-	rm -f docs/report.css
-	@echo "Cleaned generated files"


.PHONY: eval
eval: ## Run evaluations (if needed)
-	benchci evaluate


.PHONY: clean-logs
clean-logs: ## Clean log files
-	@echo "Cleaning log files..."
-   grep -rnil "BadRequestError" ./logs/ | xargs -r rm -f
-   grep -rnil "AuthenticationError" ./logs/ | xargs -r rm -f
-   grep -rnil "OpenRouterError" ./logs/ | xargs -r rm -f
-   grep -rnil "JSONDecodeError" ./logs/ | xargs -r rm -f


.PHONY: backup
backup: ## Backup the database
-	@echo "Backing up database..."
-   cp -rf ./logs/* ./.originals/
