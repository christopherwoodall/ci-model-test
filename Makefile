# Makefile for serving the GitHub Pages site locally

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  serve    - Serve the site locally for preview"
	@echo "  build    - Build the database and React components"
	@echo "  clean    - Clean generated files"

# Serve the site locally
.PHONY: serve
serve: build
	@echo "Serving site at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	cd docs && python3 -m http.server 8000

# Build the database and React components
.PHONY: build
build:
	python3 build_pages.py

# Clean generated files
.PHONY: clean
clean:
	rm -f docs/database.json
	rm -f docs/ReportPage.js
	rm -f docs/ReportPage.css
	@echo "Cleaned generated files"

# Install dependencies (if needed)
.PHONY: install
install:
	pip install -r requirements.txt

# Run evaluations (if needed)
.PHONY: eval
eval:
	python3 evaluation.py --config config.yaml