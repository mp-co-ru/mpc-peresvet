import os
from ldap3 import Server, Connection, SAFE_SYNC

server_uri = os.getenv("LDAP_URI")
server = Server(server_uri)
uid = os.getenv("LDAP_USER")
pwd = os.getenv("LDAP_PASSWORD")
conn = Connection(server, uid, pwd, client_strategy=SAFE_SYNC, auto_bind=False)