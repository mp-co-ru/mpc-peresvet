from ldap3 import SCHEMA, Server, Connection, SAFE_SYNC, ObjectDef, AttrDef

server = Server(host='localhost', port=389, get_info=SCHEMA)
read_conn = Connection(server, user='cn=admin,cn=prs', 
    password='Peresvet21', client_strategy=SAFE_SYNC, read_only=True,
    pool_name="read_ldap", pool_size=20, auto_bind=True)

o = ObjectDef('prsTag', read_conn)
print(["{}: {}".format(o._attributes[attr].name, o._attributes[attr].oid_info.syntax) for attr in o._attributes])
#a = AttrDef(o._attributes)
#r += 'MUST: ' + ', '.join(sorted([attr for attr in self._attributes if self._attributes[attr].mandatory])) + linesep
#        r += 'MAY : ' + ', '.join(sorted([attr for attr in self._attributes if not self._attributes[attr].mandatory])) + linesep