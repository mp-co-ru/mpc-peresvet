# Script launches containers in debug mode. Press F5 in VSCode after containers start to debug the app.
docker compose -f docker-compose.locust.data_get_vm_direct.yml \
    -f docker-compose.victoriametrics.yml up \
    --detach
