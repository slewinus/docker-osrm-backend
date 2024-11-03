.PHONY: up down logs help

up:
    docker compose up -d

down:
    docker compose down

logs:
    docker compose logs -f

help:
    @echo "up: Start the containers"
    @echo "down: Stop the containers"
    @echo "logs: Show the logs"
    @echo "help: Show this help message"