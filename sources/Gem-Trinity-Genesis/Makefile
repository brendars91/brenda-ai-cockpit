.PHONY: help install install-dev update-deps test test-cov lint format clean run-backend run-frontend docker-up docker-down docker-logs backup-deps

# Default target
.DEFAULT_GOAL := help

# Project directories
BACKEND_DIR := local-watcher
FRONTEND_DIR := frontend
TESTS_DIR := tests

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

##@ General

help: ## Show this help message
	@echo '$(BLUE)Gem Trinity Genesis - Development Commands$(NC)'
	@echo ''
	@echo '$(YELLOW)Usage:$(NC)'
	@echo '  make <target>'
	@echo ''
	@echo '$(YELLOW)Available targets:$(NC)'
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

##@ Development

install: ## Install all dependencies (backend + frontend)
	@echo '$(BLUE)Installing dependencies...$(NC)'
	pip install -r requirements.txt
	cd $(FRONTEND_DIR) && npm install

install-dev: ## Install development dependencies
	@echo '$(BLUE)Installing development dependencies...$(NC)'
	pip install -r requirements.txt
	pip install pip-tools pytest pytest-cov black isort bandit mypy pre-commit
	cd $(FRONTEND_DIR) && npm install

update-deps: ## Update dependency lockfiles
	@echo '$(BLUE)Updating dependency lockfiles...$(NC)'
	pip-compile requirements.in --output-file=requirements.txt --upgrade
	cd $(BACKEND_DIR) && pip-compile requirements.in --output-file=requirements.txt --upgrade
	@echo '$(GREEN)✓ Dependencies updated$(NC)'

##@ Testing

test: ## Run all tests
	@echo '$(BLUE)Running tests...$(NC)'
	cd $(BACKEND_DIR) && python -m pytest tests/ -v

test-cov: ## Run tests with coverage report
	@echo '$(BLUE)Running tests with coverage...$(NC)'
	cd $(BACKEND_DIR) && python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term
	@echo '$(GREEN)✓ Coverage report generated: htmlcov/index.html$(NC)'

test-unit: ## Run unit tests only
	@echo '$(BLUE)Running unit tests...$(NC)'
	cd $(BACKEND_DIR) && python -m pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@echo '$(BLUE)Running integration tests...$(NC)'
	cd $(BACKEND_DIR) && python -m pytest tests/integration/ -v

##@ Code Quality

lint: ## Run linters (black, isort, mypy, bandit)
	@echo '$(BLUE)Running linters...$(NC)'
	black --check .
	isort --check-only .
	bandit -r $(BACKEND_DIR)/
	@echo '$(GREEN)✓ All checks passed$(NC)'

lint-py: ## Run Python linters only
	@echo '$(BLUE)Running Python linters...$(NC)'
	black --check $(BACKEND_DIR)/
	isort --check-only $(BACKEND_DIR)/
	mypy $(BACKEND_DIR)/ --ignore-missing-imports
	bandit -r $(BACKEND_DIR)/

lint-ts: ## Run TypeScript linters
	@echo '$(BLUE)Running TypeScript linters...$(NC)'
	cd $(FRONTEND_DIR) && npm run lint

format: ## Format code (black, isort)
	@echo '$(BLUE)Formatting code...$(NC)'
	black .
	isort .
	@echo '$(GREEN)✓ Code formatted$(NC)'

format-py: ## Format Python code only
	@echo '$(BLUE)Formatting Python code...$(NC)'
	black $(BACKEND_DIR)/
	isort $(BACKEND_DIR)/

format-ts: ## Format TypeScript code
	@echo '$(BLUE)Formatting TypeScript code...$(NC)'
	cd $(FRONTEND_DIR) && npm run lint -- --fix

##@ Running the Application

run-backend: ## Run backend server (FastAPI)
	@echo '$(BLUE)Starting backend server...$(NC)'
	cd $(BACKEND_DIR) && python api_server.py

run-frontend: ## Run frontend dev server (Next.js)
	@echo '$(BLUE)Starting frontend dev server...$(NC)'
	cd $(FRONTEND_DIR) && npm run dev

run-dev: ## Run both backend and frontend (in parallel)
	@echo '$(BLUE)Starting development servers...$(NC)'
	@make -j2 run-backend run-frontend

##@ Docker

docker-up: ## Start Docker containers
	@echo '$(BLUE)Starting Docker containers...$(NC)'
	docker-compose up -d
	@echo '$(GREEN)✓ Containers started$(NC)'

docker-down: ## Stop Docker containers
	@echo '$(BLUE)Stopping Docker containers...$(NC)'
	docker-compose down
	@echo '$(GREEN)✓ Containers stopped$(NC)'

docker-logs: ## Show Docker container logs
	docker-compose logs -f

docker-restart: docker-down docker-up ## Restart Docker containers

docker-build: ## Rebuild Docker images
	@echo '$(BLUE)Rebuilding Docker images...$(NC)'
	docker-compose build
	@echo '$(GREEN)✓ Images built$(NC)'

##@ Maintenance

clean: ## Clean temporary files and caches
	@echo '$(BLUE)Cleaning temporary files...$(NC)'
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	@echo '$(GREEN)✓ Cleaned temporary files$(NC)'

clean-all: clean ## Clean everything including node_modules and .venv
	@echo '$(BLUE)Deep cleaning...$(NC)'
	rm -rf $(FRONTEND_DIR)/node_modules
	rm -rf $(FRONTEND_DIR)/.next
	rm -rf .venv
	@echo '$(GREEN)✓ Deep clean completed$(NC)'

backup-deps: ## Backup current dependencies
	@echo '$(BLUE)Backing up dependencies...$(NC)'
	cp requirements.txt requirements.txt.backup
	cp $(FRONTEND_DIR)/package.json $(FRONTEND_DIR)/package.json.backup
	@echo '$(GREEN)✓ Dependencies backed up$(NC)'

##@ Deployment

deploy: ## Deploy to production (configure your deploy command)
	@echo '$(BLUE)Deploying to production...$(NC)'
	@echo '$(YELLOW)Configure your deploy command in Makefile$(NC)'
	# Add your deployment command here
	# Example: git push origin main && ssh server 'cd /app && git pull && docker-compose up -d --build'

##@ Git

git-status: ## Show git status
	@echo '$(BLUE)Git status:$(NC)'
	git status

git-push: ## Commit and push changes (will prompt for commit message)
	@echo '$(BLUE)Committing and pushing changes...$(NC)'
	@read -p "Commit message: " msg; \
	git add -A && \
	git commit -m "$$msg" && \
	git push origin main
