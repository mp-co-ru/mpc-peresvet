import os
from logging import Logger
from pydantic import create_model, BaseModel
from typing import Dict, List, Type
from ldap3 import LEVEL, DEREF_NEVER
from app.svc.logger.PrsLogger import PrsLogger
import app.svc.ldap.ldap_db as ld
from app.models.DataStorage import PrsDataStorageEntry
from app.models.data_storages.vm import PrsVictoriametricsEntry

class Services:
    logger: Logger
    ldap: ld.PrsLDAP
    """
    Datastorages cache: 
    {
        "<ds_id>": <class PrsDataStorageEntry ..
            tags_cache: {}
        >
    }
    """
    data_storages: Dict[str, PrsDataStorageEntry]
    """
    Tags cache:
    {
        "<tag_id>": {
            "data_storage": "<data_storage_id>"
        }
    }
    """
    tags: Dict[str, Dict[str, str]]

    config = {
        "LDAP_BASE_NODE": os.getenv("LDAP_BASE_NODE", "cn=prs"),
        "LDAP_TAGS_NODE": "cn=tags,{}".format(os.getenv("LDAP_BASE_NODE", "cn=prs")),
        "LDAP_DATASTORAGES_NODE": "cn=dataStorages,{}".format(os.getenv("LDAP_BASE_NODE", "cn=prs")),
        "LDAP_DATASOURCES_NODE": "cn=dataSources,{}".format(os.getenv("LDAP_BASE_NODE", "cn=prs")),
        "LDAP_OBJECTS_NODE": "cn=objects,{}".format(os.getenv("LDAP_BASE_NODE", "cn=prs")),
    }

    @classmethod
    def set_logger(cls):
        cls.logger = PrsLogger.make_logger()

    @classmethod
    def set_ldap(cls):
        cls.ldap = ld.PrsLDAP(os.getenv("LDAP_HOST"), int(os.getenv("LDAP_PORT")), os.getenv("LDAP_USER"), os.getenv("LDAP_PASSWORD")) 

    @classmethod
    def get_base_node_id(cls):
        pass

    @classmethod
    def set_data_storages(cls):
        cls.logger.info("Start load datastorages...")
        
        found, _, response, _ = cls.ldap.get_read_conn().search(
            search_base=cls.config["LDAP_DATASTORAGES_NODE"], 
            search_filter='(cn=*)', search_scope=LEVEL, dereference_aliases=DEREF_NEVER, 
            attributes=['entryUUID', 'prsEntityTypeCode'])
        if found:
            for item in response:
                attrs = dict(item['attributes'])
                if attrs['prsEntityTypeCode'] == 1:
                    new_ds = PrsVictoriametricsEntry(cls.ldap.get_read_conn(), id=attrs['entryUUID'])
                    cls.data_storages[attrs['entryUUID']] = new_ds
        else:
            cls.data_storages = {}
        
        cls.logger.info("Datastorages loaded.")