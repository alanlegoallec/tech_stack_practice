#!/bin/bash

set -euo pipefail

echo "# Stop and remove containers, networks, volumes, and images created by docker-compose"
docker compose down -v --remove-orphans || true

echo "# Stop and remove all containers"
containers=$(docker ps -aq)
if [ -n "$containers" ]; then
    docker stop $containers || true
    docker rm -f $containers || true
else
    echo "No containers to remove."
fi

echo "# Remove unused networks"
networks=$(docker network ls -q)
if [ -n "$networks" ]; then
    docker network rm $networks || true
else
    echo "No networks to remove."
fi

echo "# Remove unused volumes"
volumes=$(docker volume ls -q)
if [ -n "$volumes" ]; then
    docker volume rm $volumes || true
else
    echo "No volumes to remove."
fi

echo "# Remove unused images"
images=$(docker images -q)
if [ -n "$images" ]; then
    docker rmi -f $images || true
else
    echo "No images to remove."
fi

echo "# Prune Docker system"
docker system prune -a -f || true
docker builder prune -f || true
docker image prune -f || true
docker container prune -f || true
docker volume prune -f || true
docker network prune -f || true
