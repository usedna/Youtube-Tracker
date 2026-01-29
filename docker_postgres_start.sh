#!/bin/bash

ERR_SERVICE_MSG="Error:Failed to start docker sevice."
ERR_COMPOSE_MSG="Error:Failed to create and run containers"
SCC_SERVICE_MSG="Docker Service was enabled successfully"
SCC_COMPOSE_MSG="Containers were created successfully"

check_success() {
    if [ $? -ne 0 ]; then
        echo "$1"
        exit 1
    else
        echo "$2"
    fi
}

if systemctl is-active --quiet docker; then
    echo "Docker Service is active"
else
    echo "Docker Service is disabled. Proceed to enable the service..."
    sudo systemctl enable --now docker

    check_success "$ERR_SERVICE_MSG" "$SCC_SERVICE_MSG"
fi


if [ ! "$(docker ps -a -q -f name=yt_postgres-db)" ] || [ "$(docker ps -aq -f status=exited -f name=yt_postgres)" ]; then
    docker compose up -d
    check_success "$ERR_COMPOSE_MSG" "$SCC_COMPOSE_MSG"
else 
    echo "The containers are running already"
fi

