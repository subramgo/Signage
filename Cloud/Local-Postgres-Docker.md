## Setup local postgres docker

docker pull postgres:10

mkdir -p $HOME/docker/volumes/postgres

docker run --rm   --name pg-docker -e POSTGRES_PASSWORD=docker -d -p 5432:5432 -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data  postgres



