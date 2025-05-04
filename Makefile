# Target to start containers in remote debug mode
debug-remote:
	docker compose -f docker-compose.yaml -f docker-compose.debug-remote.yaml --profile debug-remote up --build -d

# Target to start containers in internal debug mode - debugging from within the container
debug-internal:
	docker compose -f docker-compose.yaml -f docker-compose.debug-internal.yaml --profile debug-internal up --build -d

# Target to start containers in dev mode
dev:
	docker compose -f docker-compose.yaml --profile dev up --build -d

# Target to start containers in production mode
prod:
	docker compose -f docker-compose.yaml --profile prod up --build -d

# Clean up Docker containers, networks, volumes, and images
clean:
	@bash scripts/clean_docker.sh
	@bash scripts/unset_env.sh

clear-env:
	@bash scripts/unset_env.sh

# Makefile entry to copy install-vscode-extensions.sh to backend and frontend
copy-vscode-extensions-install-script:
	@echo "Copying install-vscode-extensions.sh to backend and frontend scripts directories..."
	cp scripts/install-vscode-extensions.sh backend/scripts/
	cp scripts/install-vscode-extensions.sh frontend/scripts/
	@echo "Successfully copied install-vscode-extensions.sh to backend and frontend!"

test-coverage:
	docker compose -f docker-compose.yaml --profile dev run --rm tests pytest --cov=backend --cov-report=xml --cov-report=term-missing --cov-fail-under=85
