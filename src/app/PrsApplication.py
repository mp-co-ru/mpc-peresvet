from fastapi import FastAPI

from typing import Optional, Union, List
from ldap3 import Reader, ObjectDef, BASE, DEREF_NEVER, SUBTREE

from app.svc.Services import Services as svc
from app.models.Tag import PrsTagCreate, PrsTagEntry
from app.models.DataStorage import PrsDataStorageCreate, PrsDataStorageEntry
from app.models.Data import PrsData
import app.times as times

class PrsApplication(FastAPI):
    def __init__(self, **kwargs):
        super(PrsApplication, self).__init__(**kwargs)
        svc.set_logger()
        svc.set_ldap()
        svc.set_data_storages()

    def create_tag(self, payload: PrsTagCreate) -> PrsTagEntry:
        if payload.dataStorageId is None and svc.default_data_storage_id is not None:
            payload.dataStorageId = svc.default_data_storage_id
        return PrsTagEntry(payload)

    def create_dataStorage(self, payload: PrsDataStorageCreate) -> PrsDataStorageEntry:
        if payload.data.attributes.prsDefault:
            for _, item in svc.data_storages.items():
                item.modify({"prsDefault": False})

        return PrsDataStorageEntry(data=payload)

    def read_dataStorage(self, id: str) -> PrsDataStorageEntry:
        return PrsDataStorageEntry(id=id)

    def read_tag(self, id: str) -> PrsTagEntry:
        return PrsTagEntry(id=id)
    
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

    async def data_set(self, data: PrsData):
        """
        Метод разбивает массив данных на несколько массивов: один массив - одно хранилище и раздаёт эти массивы на запись 
        соответствующим хранилищам. Также создаёт метки времени, если их нет и конвертирует их в микросекунды.
        """
        now_ts = times.now_int()
        # словарь значений для записи в разных хранилищах
        # имеет вид:
        # {
        #   "<data_storge_id>": {
        #        "<tag_id>": [(x, y, q)]
        #   }            
        # }
        data_storages = {}
        for tag_item in data['data']:
            data_storage_id = svc.tags[tag_item.tagId]["data_storage"]
            data_storages.setdefault(data_storage_id, {})
            data_storages[data_storage_id].setdefault(tag_item.tagId, [])

            for data_item in tag_item.data:
                x = (now_ts, times.timestamp_to_int(data_item.x))[data_item.x is not None]
                data_storages[data_storage_id][tag_item.tagId].append((x, data_item.y, data_item.q))

        # TODO: сделать параллельный запуск записи для хранилищ, а не друг за другом (background_tasks?)
        for key, value in data_storages.items():
            await svc.data_storages[key].set_data(value)
