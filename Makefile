# Target to start containers in remote debug mode
debug-remote:
	docker compose -f docker-compose.yaml -f docker-compose.debug-remote.yaml --profile debug-remote up --build

# Target to start containers in internal debug mode - debugging from within the container
debug-internal:
	docker compose -f docker-compose.yaml -f docker-compose.debug-internal.yaml --profile debug-internal up --build -d

# Target to start containers in production mode
prod:
	docker compose -f docker-compose.yaml --profile prod up --build -d

# Target to start containers in development mode
clean:
    # Stop and remove containers, networks, volumes, and images created by `docker-compose`
    docker compose down -v --remove-orphans || true

    # Force stop and remove all containers (running or stopped)
    echo "Checking for containers..."
    docker ps -aq  # This will list all container IDs
    if [ "$(docker ps -aq | tr -d '\n')" ]; then \
        echo "Stopping and removing all containers..."; \
        docker stop $(docker ps -aq); \
        docker rm -f $(docker ps -aq); \
    else \
        echo "No containers to stop/remove."; \
    fi

    # Remove unused networks
    if [ "$(docker network ls -q)" ]; then \
        echo "Removing unused networks..."; \
        docker network rm $(docker network ls -q); \
    else \
        echo "No networks to remove."; \
    fi

    # Remove unused volumes
    if [ "$(docker volume ls -q)" ]; then \
        echo "Removing unused volumes..."; \
        docker volume rm $(docker volume ls -q); \
    else \
        echo "No volumes to remove."; \
    fi

    # Remove unused images
    if [ "$(docker images -q)" ]; then \
        echo "Removing unused images..."; \
        docker rmi -f $(docker images -q); \
    else \
        echo "No images to remove."; \
    fi

    # Prune unused Docker system resources (containers, images, volumes, etc.)
    docker system prune -a -f
    docker builder prune -f
    docker image prune -f
    docker container prune -f
    docker volume prune -f
    docker network prune -f
