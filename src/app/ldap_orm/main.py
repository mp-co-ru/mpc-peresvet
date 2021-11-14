from ldap3 import Server, Connection, SAFE_SYNC


server = Server('my_server')
conn = Connection(server, 'my_user', 'my_password', client_strategy=SAFE_SYNC, auto_bind=True)
status, result, response, _ = conn.search('o=test', '(objectclass=*)')  # usually you don't need the original request (4th element of the return tuple)

