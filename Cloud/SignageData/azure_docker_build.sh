docker build -t azure-data-service .
docker tag azure-data-service midmarkettestm8195129533.azurecr.io/signage/data-service

# After azure login
docker push midmarkettestm8195129533.azurecr.io/signage/data-service


