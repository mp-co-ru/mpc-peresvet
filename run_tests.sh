docker-compose -f docker-compose.yml -f docker-compose.test.yml stop
docker rm -f ldap_test
docker-compose -f docker-compose.yml -f docker-compose.test.yml build
docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d
docker-compose exec peresvet pytest --cov=./app . 