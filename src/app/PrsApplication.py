from fastapi import FastAPI, HTTPException

from ldap3 import BASE, DEREF_ALWAYS, DEREF_NEVER, SUBTREE, LEVEL
from typing import Dict, Any

from app.svc.Services import Services as svc
from app.models.Tag import PrsTagEntry, PrsTagCreate
from app.models.DataStorage import PrsDataStorageEntry, PrsDataStorageCreate
from app.models.data_storages.vm import PrsVictoriametricsEntry
from app.models.Data import PrsData
import app.times as times
from app.const import *

class PrsApplication(FastAPI):
    def __init__(self, **kwargs):
        super(PrsApplication, self).__init__(**kwargs)
        svc.set_logger()
        svc.set_ldap()

        self._set_data_storages()

    def _reg_data_storage_in_cache(self, ds: PrsDataStorageEntry):
        """
        Метод, заносящий в кэш хранилище данных. 
        Вызывается при создании нового хранилища и при старте приложения.
        """
        svc.data_storages[ds.id] = ds
        if ds.data.attributes.prsDefault:
            svc.default_data_storage_id = ds.id
    
    def get_tag_cache(self, tag_id: str, key: str) -> Any:
        if self.tags.get(tag_id) is not None:
            return self.tags[tag_id].get(key)

    def _set_data_storages(self):
        svc.logger.info("Start load datastorages...")
        
        found, _, response, _ = svc.ldap.get_read_conn().search(
            search_base=svc.config["LDAP_DATASTORAGES_NODE"], 
            search_filter='(cn=*)', search_scope=LEVEL, dereference_aliases=DEREF_NEVER, 
            attributes=['entryUUID', 'prsEntityTypeCode', 'prsDefault'])
        if found:
            for item in response:
                attrs = dict(item['attributes'])
                
                if attrs['prsEntityTypeCode'] != CN_DS_VICTORIAMETRICS:
                    continue
                
                new_ds = PrsVictoriametricsEntry(id=attrs['entryUUID'])
                self._reg_data_storage_in_cache(new_ds)

                if attrs['prsDefault']:
                    svc.default_data_storage_id = attrs['entryUUID']
        
        if svc.data_storages:
            if svc.default_data_storage_id is None:
                svc.default_data_storage_id = svc.data_storages.keys()[0]
        
        svc.logger.info("Хранилища данных загружены.")

    def create_tag(self, payload: PrsTagCreate) -> PrsTagEntry:
        if not svc.data_storages:
            svc.logger.info("Невозможно создать тэг без зарегистрированных хранилищ данных.")
            raise HTTPException(status_code=424, detail="Перед созданием тэга необходимо зарегистрировать хотя бы одно хранилище данных.")

        if payload.dataStorageId is None:
            payload.dataStorageId = svc.default_data_storage_id
        new_tag = PrsTagEntry(payload)

        svc.data_storages[payload.dataStorageId].reg_tags(new_tag)

        svc.logger.info("Тэг '{}'({}) создан.".format(new_tag.data.attributes.cn, new_tag.id))

        return new_tag

    def create_dataStorage(self, payload: PrsDataStorageCreate) -> PrsDataStorageEntry:
        if payload.attributes.prsDefault:
            for _, item in svc.data_storages.items():
                item.modify({"prsDefault": False})

        if not svc.data_storages:
            if not payload.attributes.prsDefault:
                payload.attributes.prsDefault = True

        if payload.attributes.prsEntityTypeCode != CN_DS_VICTORIAMETRICS:
            raise HTTPException(status_code=422, detail="Поддерживается только создание хранилища Victoriametrics (prsEntityTypeCode = 1)")
        
        new_ds = PrsVictoriametricsEntry(data=payload)
        self._reg_data_storage_in_cache(new_ds)

        svc.logger.info("Хранилище данных '{}'({}) создано.".format(new_ds.data.attributes.cn, new_ds.id))

        return new_ds

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
        for tag_item in data.data:
            data_storage_id = svc.tags[tag_item.tagId]["data_storage"]
            if data_storages.get(data_storage_id) is None:
                data_storages[data_storage_id] = {}
            data_storages[data_storage_id].setdefault(tag_item.tagId, [])

            for data_item in tag_item.data:
                x = (now_ts, times.timestamp_to_int(data_item.x))[data_item.x is not None]
                data_storages[data_storage_id][tag_item.tagId].append((x, data_item.y, data_item.q))

        # TODO: сделать параллельный запуск записи для хранилищ, а не друг за другом (background_tasks?)
        for key, value in data_storages.items():
            await svc.data_storages[key].set_data(value)
