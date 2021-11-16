import os
from logging import Logger
from pydantic import create_model, BaseModel
from typing import List, Type
from ldap3 import ObjectDef, AttrDef, Connection, Entry
from ..logger.PrsLogger import PrsLogger
import app.ldap.ldap_db as ld
import app.models.models as m


class Services:
    logger: Logger
    ldap: ld.PrsLDAP

    @classmethod
    def set_logger(cls):
        cls.logger = PrsLogger.make_logger()

    @classmethod
    def set_ldap(cls):
        cls.ldap = ld.PrsLDAP(os.getenv("LDAP_HOST"), int(os.getenv("LDAP_PORT")), os.getenv("LDAP_USER"), os.getenv("LDAP_PASSWORD")) 