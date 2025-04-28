# Target to start containers in remote debug mode
debug-remote:
	docker compose -f docker-compose.yaml -f docker-compose.debug-remote.yaml --profile debug-remote up --build

# Target to start containers in internal debug mode - debugging from within the container
debug-internal:
	docker compose -f docker-compose.yaml -f docker-compose.debug-internal.yaml --profile debug-internal up --build -d

# Target to start containers in production mode
prod:
	docker compose -f docker-compose.yaml --profile prod up --build -d

# Clean up Docker containers, networks, volumes, and images
clean:
	@bash scripts/clean_docker.sh
