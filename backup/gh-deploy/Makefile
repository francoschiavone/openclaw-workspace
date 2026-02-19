.PHONY: help up down logs restart clean test build

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs (follow mode)
	docker-compose logs -f

restart: ## Restart all services
	docker-compose restart

clean: ## Stop and remove all containers, networks, and volumes
	docker-compose down -v
	docker system prune -f

build: ## Build backend image
	docker-compose build backend

test: ## Run backend tests
	cd backend && pytest -v

ps: ## Show service status
	docker-compose ps

health: ## Check service health
	@echo "Backend: $$(curl -s http://localhost:8000/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "Ditto: $$(curl -s http://localhost:8080/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"

shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/bash

shell-mongo: ## Open MongoDB shell
	docker-compose exec mongodb mongosh -u ditto -p ditto

create-example: ## Create an example digital twin
	curl -X POST http://localhost:8000/things/ \
		-H "Content-Type: application/json" \
		-d '{"thing_id":"com.example:sensor-01","attributes":{"type":"temperature-sensor"},"features":{"temperature":{"properties":{"value":22.5,"unit":"celsius"}}}}'
