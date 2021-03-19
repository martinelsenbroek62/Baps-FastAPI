
.PHONY: help precommit build clean codemetrics lint logdir format run-dev securitycheck tests

PR := '^.*\(__pycache__\|\.py[co]\)$$'
GIT_BRANCH = $$(git symbolic-ref --short HEAD)


help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## Build the development and app container images
	docker-compose build
	docker-compose -f docker-compose.dev.yml build

clean: ## Clean the project environment (remove cached Python files, logs, etc.)
	find . -regex $(PR) -delete
	rm -rf logs

devserver: ## Run the development server with uvicorn
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

lint: logdir ## Run the pylint tool and send results to logs/
	find . -iname "*.py" -not -path "./jobs/*" | xargs pylint > logs/pylint.txt

logdir:
	test -d logs || mkdir logs

format: ## Run black auto-format tool
	black . --target-version py38 --exclude it/templates/*.py

formatcheck: ## Run black auto-format tool in "check" mode
	black . --check --target-version py38 --exclude it/templates/*.py

securitycheck: logdir ## Run securit scans (safety, bandit) and send results to logs/
	safety check --full-report > ./logs/safety.txt && \
	bandit .  --recursive --format txt  --output ./logs/bandit.txt --skip B101

tests: logdir ## Run unit tests and send results to logs/
	pytest tests --verbose --junit-xml logs/unittest-results.xml

up: ## Run the development container mounting the project directory
	docker-compose -f docker-compose.dev.yml up

down: ## Down docker-compose dev command
	docker-compose -f docker-compose.dev.yml down