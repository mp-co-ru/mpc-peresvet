import os
from logging import Logger
from pydantic import create_model, BaseModel
from typing import List, Type
from ldap3 import ObjectDef, AttrDef, Connection, Entry
from ..logger.PrsLogger import PrsLogger
import app.ldap.ldap_db as ld


class Services:
    logger: Logger
    ldap: ld.PrsLDAP

    # типы сущностей для валидации запросов
    PrsModelNode: None
    PrsTag: None
    
    # данные для преобразования синтаксисов LDAP в типы Python
    str_syntax = [None, '1.3.6.1.4.1.1466.115.121.1.15']
    bool_syntax = ['1.3.6.1.4.1.1466.115.121.1.7']
    int_syntax = ['1.3.6.1.4.1.1466.115.121.1.27']
    float_syntax = ['1.3.6.1.4.1.1466.115.121.1.5']

    # данные по дефолтным значениям для классов
    defaults = {
        'prsTag': {
            'prsTagArchive': True,
            'prsTagCompress': True,
            'prsTagStep': False,
            'prsTagUpdate': True,
            'prsValueTypeCode': 0,
            'prsActive': True
        }
    }

    @classmethod
    def set_logger(cls):
        cls.logger = PrsLogger.make_logger()

    @classmethod
    def set_ldap(cls):
        cls.ldap = ld.PrsLDAP(os.getenv("LDAP_HOST"), int(os.getenv("LDAP_PORT")), os.getenv("LDAP_USER"), os.getenv("LDAP_PASSWORD")) 

    @classmethod
    def _initialize_type(cls, conn: Connection, name: str) -> Type['BaseModel']:
        """Метод создаёт pydantic BaseModel для валидации передаваемых данных.
        Так как схема OpenLDAP не поддерживает значения атрибутов по умолчанию, то эти значения приходится кодировать.
        Также проблема с конвертацией типов LDAP в типы python. Тоже кодируем.
        """
        o = ObjectDef(name, conn)
        fields = {}
        class_defaults = cls.defaults.get(name, {})
        for attr in o._attributes:
            if attr == 'objectClass':
                continue
                        
            python_type = str
            default = class_defaults.get(attr)
            if default is None and o._attributes[attr].mandatory:
                default = ...
            if attr == 'prsJsonConfigString':
                python_type = dict
            else:
                syntax = o._attributes[attr].oid_info.syntax
                if syntax in cls.str_syntax:
                    python_type = str
                elif syntax in cls.int_syntax:
                    python_type = int
                elif syntax in cls.float_syntax:
                    python_type = float
                elif syntax in cls.bool_syntax:
                    python_type = bool
            if not o._attributes[attr].single_value:
                python_type = List[python_type]

            fields[name] = (python_type, default)

    @classmethod
    def initialize_types(cls):
        conn = cls.ldap.get_read_conn()
        cls.PrsModelNode = cls._initialize_type(conn, 'prsModelNode')
        cls.PrsTag = cls._initialize_type(conn, 'prsTag')
        
        