# Target to start containers in remote debug mode
debug-remote:
	docker compose -f docker-compose.yaml -f docker-compose.debug-remote.yaml --profile debug-remote up --build

# Target to start containers in internal debug mode - debugging from within the container
debug-internal:
	docker compose -f docker-compose.yaml -f docker-compose.debug-internal.yaml --profile debug-internal up --build

# Target to start containers in production mode
prod:
	docker compose -f docker-compose.yaml --profile prod up --build

# Target to clean up Docker resources
clean:
	docker compose down -v --remove-orphans
	@if [ "$(docker ps -aq)" ]; then \
		docker rm -f $(docker ps -aq); \
	else \
		echo "No containers to remove."; \
	fi
	@if [ "$(docker images -q)" ]; then \
		docker rmi -f $(docker images -q); \
	else \
		echo "No images to remove."; \
	fi
	@if [ "$(docker volume ls -q)" ]; then \
		docker volume rm $(docker volume ls -q); \
	else \
		echo "No volumes to remove."; \
	fi
	docker network prune -f
	docker system prune -f
	docker builder prune -f
	docker image prune -f
	docker container prune -f
	docker volume prune -f
