# Signage Web Services

## Setup

  1. Run `install.sh`
  2. Configure upload user in `/opt/signage/web.yml`

### Setup Docker on a fresh instance

  1. Based docker image `docker build -t ubuntu-akshi:latest -f Dockerfile.base .`
  2. App docker image `docker build -t akshi:latest -f Dockerfile.app .`
  3. Run docker image `docker run -d -p 5000:5000 akshi:latest`

  4. Check runing image `docker ps`

### Update docker on a running instance

  1. Copy the database before pushing a new instance. 
  `docker cp <CONTAINER ID>:/Akshi/akshi.db  <backup location>`
  2. Stop the running container `docker stop <CONTAINER ID>`
  2. Continue from step 2 listed in the previous section.


