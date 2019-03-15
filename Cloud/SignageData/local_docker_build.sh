
# Create a network
docker network create --driver=bridge --subnet=192.168.11.0/29 --gateway=192.168.11.1  signage_network

# Run postgres docker
docker run --rm   --network signage_network --ip "192.168.11.2" --name pg-docker -e POSTGRES_PASSWORD=docker -d -p 5432:5432 -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data  postgres:10

# Run the data sevice docker
docker build -t data-service .
docker run -p 5000:5000  --network signage_network --ip "192.168.11.3" -d data-service


