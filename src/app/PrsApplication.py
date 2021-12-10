from fastapi import FastAPI

from typing import Optional, Union, List
from ldap3 import Reader, ObjectDef, BASE, DEREF_NEVER, SUBTREE

from app.svc.Services import Services as svc
from app.models.Tag import PrsTagCreate, PrsTagEntry
from app.models.DataStorage import PrsDataStorageCreate, PrsDataStorageEntry

class PrsApplication(FastAPI):
    def __init__(self, **kwargs):
        super(PrsApplication, self).__init__(**kwargs)
        svc.set_logger()
        svc.set_ldap()

    def create_tag(self, payload: PrsTagCreate) -> PrsTagEntry:
        return PrsTagEntry(svc.ldap.get_write_conn(), payload)

    def create_dataStorage(self, payload: PrsDataStorageCreate) -> PrsDataStorageEntry:
        return PrsDataStorageEntry(conn=svc.ldap.get_write_conn(), data=payload)

    def read_dataStorage(self, id: str) -> PrsDataStorageEntry:
        return PrsDataStorageEntry(conn=svc.ldap.get_read_conn(), id=id)

    def read_tag(self, id: str) -> PrsTagEntry:
        return PrsTagEntry(svc.ldap.get_read_conn(), id=id)
    
    def get_node_id_by_dn(self, dn: str) -> str:
        found, _, response, _ = svc.ldap.get_read_conn().search(
            search_base=dn, search_filter='(cn=*)', search_scope=BASE, dereference_aliases=DEREF_NEVER, attributes='entryUUID')
        if found:
            return response[0]['attributes']['entryUUID']
        else:
            return None

    def get_node_dn_by_id(self, id: str) -> str:
        found, _, response, _ = svc.ldap.get_read_conn().search(
            search_base=svc.config["LDAP_BASE_NODE"],
            search_filter="({}={})".format('entryUUID', id),
            search_scope=SUBTREE,
            dereference_aliases=False,
            attributes='cn'
        )

        return response[0]['dn'] if found else None