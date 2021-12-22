from fastapi import FastAPI

from ldap3 import BASE, DEREF_ALWAYS, DEREF_NEVER, SUBTREE, LEVEL
from typing import Dict, Any

from app.svc.Services import Services as svc
from app.models.Tag import PrsTagEntry, PrsTagCreate
from app.models.DataStorage import PrsDataStorageEntry, PrsDataStorageCreate
from app.models.data_storages.vm import PrsVictoriametricsEntry
from app.models.Data import PrsData
import app.times as times

class PrsApplication(FastAPI):
    def __init__(self, **kwargs):
        super(PrsApplication, self).__init__(**kwargs)
        svc.set_logger()
        svc.set_ldap()

        """
        Datastorages cache: 
        {
            "<ds_id>": <class PrsDataStorageEntry ..>
        }
        """
        self.data_storages: Dict[str, PrsDataStorageEntry] = {}
        self.default_data_storage_id: str = None
        """
        Tags cache:
        {
            "<tag_id>": {
                "app": {
                    "dataStorageId": "<ds_id>"
                }
                "data_storage": Any(some_value)
            }
        }
        Кэшем пользуется не только само приложение, но и разные сущности.
        То есть к ключу с id тэга сущности могут привязывать свои кэши.
        Для этого они вызывают метод set_tag_cache.
        Для получения нужного значения - get_tag_cache.
        Для удобства примем, что каждая сущность создаёт кэш с ключом, имя которого - похоже на имя сущности, а значение - любое нужное сущности.
        Приложение создаёт ключ "app", PrsDataStorageEntry создает ключ "data_storage"... 

        """
        self.tags: Dict[str, Dict[str, Any]] = {}

        self._set_data_storages()

    def set_tag_cache(self, tag: PrsTagEntry, key: str, value: Any):
        """
        Метод используется приложением и разными сущностями для формирования кэша тэгов.
        Методу передаётся PrsTagEntry, чтообы приложение могло сформировать свои кэши для тэга.
        """
        self.tags.setdefault(tag.id, {"app": {"dataStorageId": tag.data.dataStorageId}})
        self.tags[tag.id][key] = value
    
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
                
                if attrs['prsEntityTypeCode'] != 1:
                    continue
                
                new_ds = PrsVictoriametricsEntry(svc.ldap.get_read_conn(), id=attrs['entryUUID'])
                self.data_storages[attrs['entryUUID']] = new_ds

                if attrs['prsDefault']:
                    self.default_data_storage_id = attrs['entryUUID']
        
        if self.data_storages:
            if self.default_data_storage_id is None:
                self.default_data_storage_id = self.data_storages.keys()[0]
        
        svc.logger.info("Datastorages loaded.")

    def create_tag(self, payload: PrsTagCreate) -> PrsTagEntry:
        if payload.dataStorageId is None and self.default_data_storage_id is not None:
            payload.dataStorageId = self.default_data_storage_id
        new_tag = PrsTagEntry(payload)

        if payload.dataStorageId:
            self.data_storages[payload.dataStorageId].reg_tags(new_tag.id)

        return new_tag

    def create_dataStorage(self, payload: PrsDataStorageCreate) -> PrsDataStorageEntry:
        if payload.attributes.prsDefault:
            for _, item in self.data_storages.items():
                item.modify({"prsDefault": False})

        if not self.data_storages:
            if not payload.attributes.prsDefault:
                payload.attributes.prsDefault = True

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
            data_storage_id = self.tags[tag_item.tagId]["data_storage"]
            data_storages.setdefault(data_storage_id, {})
            data_storages[data_storage_id].setdefault(tag_item.tagId, [])

            for data_item in tag_item.data:
                x = (now_ts, times.timestamp_to_int(data_item.x))[data_item.x is not None]
                data_storages[data_storage_id][tag_item.tagId].append((x, data_item.y, data_item.q))

        # TODO: сделать параллельный запуск записи для хранилищ, а не друг за другом (background_tasks?)
        for key, value in data_storages.items():
            await self.data_storages[key].set_data(value)
