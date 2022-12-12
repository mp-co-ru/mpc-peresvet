docker compose -f docker-compose.peresvet.yml -f docker-compose.victoriametrics.yml -f docker-compose.test.yml stop
docker rm -f ldap_test
#docker-compose -f docker-compose.peresvet.yml -f docker-compose.victoriametrics.yml -f docker-compose.test.yml build
docker compose -f docker-compose.peresvet.yml -f docker-compose.victoriametrics.yml -f docker-compose.test.yml up --build -d
docker exec peresvet pytest --cov=./app .
