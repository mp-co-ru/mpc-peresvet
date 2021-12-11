import os
from logging import Logger
from pydantic import create_model, BaseModel
from typing import Dict, List, Type
from ldap3 import ObjectDef, AttrDef, Connection, Entry
from app.svc.logger.PrsLogger import PrsLogger
import app.svc.ldap.ldap_db as ld

class Services:
    logger: Logger
    ldap: ld.PrsLDAP

    config = {
        "LDAP_BASE_NODE": os.getenv("LDAP_BASE_NODE", "cn=prs")
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