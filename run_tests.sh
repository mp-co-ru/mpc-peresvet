docker-compose -f docker-compose.yml -f docker-compose.test.yml stop
docker container rm ldap_test
docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d --build
docker-compose exec peresvet pytest --cov=./app . 