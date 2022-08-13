# Script launches containers in debug mode. Press F5 in VSCode after containers start to debug the app.
docker compose -f docker-compose.yml stop
docker compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.debug.yml up
