.PHONY: help install test lint format clean docker-build docker-run test-setup

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@sed -n 's/^##//p' $(MAKEFILE_LIST) | column -t -s ':' | sed -e 's/^/ /'

install: ## Install Python dependencies
	pip install -r requirements.txt

test: ## Run tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage
	pytest tests/ --cov=. --cov-report=html

lint: ## Run linters
	flake8 .
	mypy automation/

format: ## Format code with black
	black .

clean: ## Clean up build artifacts
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '.coverage' -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/

docker-build: ## Build Docker image
	docker build -t arcgis-knowledge-integration:latest .

docker-run: ## Run Docker container
	docker run --rm -it arcgis-knowledge-integration:latest

docker-deploy: ## Deploy using deployment script
	./scripts/deploy.sh

test-setup: ## Run setup script
	./scripts/setup.sh

.PHONY: test test-coverage lint format clean docker-build docker-run docker-deploy test-setup