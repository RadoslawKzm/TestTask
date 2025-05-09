.PHONY: up-dev
up-build:
	docker compose -f docker-compose.yaml build

.PHONY: up-dev
up-dev:
	#docker compose -f docker-compose.yaml down
	@${MAKE} down-dev
	@${MAKE} up-build
	docker compose -f docker-compose.yaml up -d

.PHONY: up-db
up-db:
	#docker compose -f docker-compose.yaml down
	@${MAKE} down-dev
	@${MAKE} up-build
	docker compose -f docker-compose.yaml up -d postgres-db

.PHONY: down-dev
down-dev:
	docker compose -f docker-compose.yaml down

.PHONY: down-dev-volumes
down-dev-volumes:
	docker compose -f docker-compose.yaml down -v

.PHONY: up-backend
up-backend:
	docker compose -f docker-compose.yaml down backend
	docker compose -f docker-compose.yaml build backend
	docker compose -f docker-compose.yaml up -d backend


##@ Testing

.PHONY: test-docker
test-docker: ## Run pytest tests in the backend Docker container
	@echo "Running pytest tests in Docker..."
	@docker compose -f docker-compose.yaml exec -T backend \
		bash -c "source /opt/venv/bin/activate && pytest /backend/api/tests/routers -v $(PYTEST_ARGS)"
	@echo "Docker pytest tests completed"