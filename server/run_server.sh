DOCKER_COMPOSE_FILE=$1
docker-compose --file $DOCKER_COMPOSE_FILE up --abort-on-container-exit --remove-orphans
#docker-compose up -d --remove-orphans
