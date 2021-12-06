from fastapi import FastAPI

from typing import Optional, Union, List
from app.svc.Services import Services as svc
from app.models.ModelNode import PrsResponseCreate
from app.models.Tag import PrsTagCreate, PrsTagEntry

class PrsApplication(FastAPI):
    def __init__(self, **kwargs):
        super(PrsApplication, self).__init__(**kwargs)
        svc.set_logger()
        svc.set_ldap()

    def create_tag(self, payload: PrsTagCreate):
        return PrsTagEntry(svc.ldap.get_write_conn(), payload)

    def read_tag(self, id: str) -> PrsTagEntry:
        return PrsTagEntry(svc.ldap.get_read_conn(), id=id)
    