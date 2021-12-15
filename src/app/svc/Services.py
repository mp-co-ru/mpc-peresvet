import os
from logging import Logger
from typing import Dict
from ldap3 import LEVEL, DEREF_NEVER
from app.svc.logger.PrsLogger import PrsLogger
import app.svc.ldap.ldap_db as ld

class Services:
    logger: Logger
    ldap: ld.PrsLDAP
    
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

    