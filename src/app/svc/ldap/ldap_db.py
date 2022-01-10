import os
from ldap3 import SCHEMA, Server, Connection, SAFE_SYNC
import app.svc.Services as svc

class PrsLDAP:
    
    def __init__(self, host: str, port: str, uid: str, pwd: str):
        svc.Services.logger.info("LDAP Server connecting...")
        self._server = Server(host=host, port=port, get_info=SCHEMA)
        svc.Services.logger.debug("uid: {}".format(uid))
        self._write_conn = Connection(
            self._server, user=uid, password=pwd, 
            client_strategy=SAFE_SYNC, read_only=False,
            pool_name="write_ldap", pool_size=1, auto_bind=True)
        self._read_conn = Connection(
            self._server, user=uid, password=pwd, 
            client_strategy=SAFE_SYNC, read_only=True, check_names=True,  
            pool_name="read_ldap", pool_size=20, auto_bind=True)
        svc.Services.logger.info("LDAP Server connected.")
    
    def get_read_conn(self, **kwargs) -> Connection:
        return self._read_conn

    def get_write_conn(self, **kwargs) -> Connection:
        return self._write_conn

    def add_alias(self, parent_dn: str, aliased_dn: str, name: str):
        obj_class = ['alias', 'extensibleObject']
        new_dn = "cn={},{}".format(name, parent_dn)
        attrs = {"cn": name, "aliasedObjectName": aliased_dn}
        self.get_write_conn().add(new_dn, object_class=obj_class, attributes=attrs)
        svc.Services.logger.debug("Alias added. Parent: {} : alias_to: {}".format(parent_dn, name))
    
    def __del__(self): 
        self._read_conn.unbind()
        self._write_conn.unbind()