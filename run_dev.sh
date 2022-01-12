# Script launches containers in dev mode. 
# Some internal ports are exposed to localhost.
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
