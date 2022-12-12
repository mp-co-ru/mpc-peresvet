# Script launches containers in debug mode. Press F5 in VSCode after containers start to debug the app.
#docker compose -f docker-compose.peresvet.yml -f docker-compose.victoriametrics.yml stop
docker compose -f docker-compose.peresvet.yml -f docker-compose.peresvet.ssl.yml -f docker-compose.nginx.yml -f docker-compose.nginx.ssl.yml -f docker-compose.victoriametrics.yml -f docker-compose.grafana.yml up
