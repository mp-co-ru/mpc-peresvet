from src.common.api_crud_settings import APICRUDSettings

class DataStoragesAPICRUDSettings(APICRUDSettings):

    #: имя сервиса
    svc_name: str = "dataStorages_api_crud"
    #: строка коннекта к RabbitMQ
    amqp_url: str = "amqp://prs:Peresvet21@rabbitmq/"
    #: строка коннекта к OpenLDAP
    ldap_url: str = "ldap://ldap:389/cn=prs????bindname=cn=admin%2ccn=prs,X-BINDPW=Peresvet21"

    #: обменник для публикаций
    publish: dict = {
        "main": {
            "name": "peresvet",
            "type": "direct",
            "routing_key": "dataStorages_api_crud_publish"
        }
    }
    consume: dict = {
        "queue_name": "dataStorages_api_crud_consume",
        "exchanges": {
            "main": {
                #: имя обменника
                "name": "peresvet",
                #: тип обменника
                "type": "direct",
                #: привзяка для очереди
                "routing_key": ["dataStorages_api_crud_consume"]
            }
        }
    }
