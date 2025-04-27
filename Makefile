# Target to start containers in debug mode
debug-remote:
    docker compose -f docker-compose.yaml -f docker-compose.debug-remote.yaml --profile debug-remote up --build

debug-from-container:
    docker compose -f docker-compose.yaml -f docker-compose.debug-internal.yaml --profile debug-internal up --build

# Target to start containers in production mode
prod:
    docker compose -f docker-compose.yaml --profile prod up --build

# Target to clean up Docker resources
clean:
    docker compose down -v --remove-orphans
    docker rm -f $(docker ps -aq)
    docker rmi -f $(docker images -q)
    docker volume rm $(docker volume ls -q)
    docker network prune -f
    docker system prune -f
    docker builder prune -f
    docker image prune -f
    docker container prune -f
    docker volume prune -f
