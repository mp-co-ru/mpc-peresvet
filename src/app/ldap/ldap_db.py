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
            client_strategy=SAFE_SYNC, read_only=True,
            pool_name="read_ldap", pool_size=20, auto_bind=True)
        svc.Services.logger.info("LDAP Server connected.")
    