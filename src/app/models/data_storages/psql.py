import json
import copy
from typing import Dict

from urllib.parse import urlparse
from fastapi import HTTPException, Response

import asyncpg as apg

from pydantic import validator, root_validator

from app.models.DataStorage import PrsDataStorageEntry, PrsDataStorageCreate
from app.models.Tag import PrsTagEntry
from app.svc.Services import Services as svc
from app.const import CNHTTPExceptionCodes as HEC, CNTagValueTypes as TVT

'''
class PrsPostgreSQLCreate(PrsDataStorageCreate):

    @root_validator
    # этот валидатор должен быть в классах конкретных хранилищ
    @classmethod
    def check_config(cls, values):

        def uri_validator(x):
            result = urlparse(x)
            return all([result.scheme, result.netloc])

        attrs = values.get('attributes')
        if not attrs:
            raise ValueError((
                "При создании хранилища необходимо задать атрибуты."
            ))

        config = attrs.get('prsJsonConfigString')

        if not config:
            raise ValueError((
                "Должна присутствовать конфигурация (атрибут prsJsonConfigString)."
            ))
            #TODO: методы класса создаются при импорте, поэтому jsonConfigString = None
            # и возникает ошибка

        try:
            if isinstance(config, str):
                config = json.loads(config)

            dsn = config["dsn"]
            if uri_validator(dsn):
                return values
        except Exception as ex:
            raise ValueError((
                "Конфигурация (атрибут prsJsonConfigString) для PostgreSQL должна быть вида:\n"
                "{'dsn': 'postgres://<user>:<password>@<host>:<port>/<database>?<option>=<value>'"
            )) from ex
'''

class PrsPostgreSQLEntry(PrsDataStorageEntry):

    def __init__(self, **kwargs):
        super(PrsPostgreSQLEntry, self).__init__(**kwargs)

        self.tag_cache = {}
        if isinstance(self.data.attributes.prsJsonConfigString, dict):
            js_config = self.data.attributes.prsJsonConfigString
        else:
            js_config = json.loads(self.data.attributes.prsJsonConfigString)

        self.dsn = js_config["dsn"]
        self.conn_pool = None

    async def _post_init(self):
        try:
            self.conn_pool = await apg.create_pool(dsn=self.dsn)
        except OSError as ex:
            er_str = f"Ошибка связи с базой данных '{self.dsn}': {ex}"
            svc.logger.error(er_str)
            raise HTTPException(HEC.CN_503, er_str) from ex

        await super(PrsPostgreSQLEntry, self)._post_init()

    def _format_tag_cache(self, tag: PrsTagEntry) -> None | str | Dict:
        # метод возращает данные, которые будут использоваться в качестве
        # кэша для тэга
        res = json.loads(tag.data.attributes.prsStore)
        res["u"] = tag.data.attributes.prsUpdate
        return res

    def _format_tag_data_store(self, tag: PrsTagEntry) -> None | Dict:

        if not tag.data.attributes.prsStore:
            return {
                'table': f"t_{tag.id}"
            }

        try:
            _ = json.loads(tag.data.attributes.prsStore)["table"]
        except json.JSONDecodeError as _:
            svc.logger.error((
                f"Для тега id:{tag.id}, dn={tag.dn} неверный формат атрибута `smtStore`. "
                "Формат атрибута: {'table': '<table_name>'}"
            ))
            return

        return json.loads(tag.data.attributes.prsStore)

    async def connect(self) -> int:
        return 0

    async def create_tag_store(self, tag: PrsTagEntry):

        async with self.conn_pool.acquire() as conn:
            tbl_name = json.loads(tag.data.attributes.prsStore)['table']

            q = (
                    f"SELECT EXISTS ("
                    f"SELECT FROM information_schema.tables "
                    f"WHERE  table_name = '{tbl_name}')"
                )
            res = await conn.fetchval(q)
            if not res:

                if tag.data.attributes.prsValueTypeCode == TVT.CN_INT:
                    s_type = "bigint"
                elif tag.data.attributes.prsValueTypeCode == TVT.CN_DOUBLE:
                    s_type = "double precision"
                elif tag.data.attributes.prsValueTypeCode == TVT.CN_STR:
                    s_type = "text"
                elif tag.data.attributes.prsValueTypeCode == TVT.CN_JSON:
                    s_type = "jsonb"
                else:
                    er_str = f"Тег: {tag.id}; неизвестный тип данных: {tag.data.attributes.prsValueTypeCode}"
                    svc.logger.error(er_str)
                    raise HTTPException(HEC.CN_422, er_str)
            # -------------------------------------------------------------------------

                # Запрос на создание таблицы в РСУБД
                query = (f'CREATE TABLE public."{tbl_name}" ('
                    f'"id" serial primary key,'
                    f'"x" bigint NOT NULL,'
                    f'"y" {s_type},'
                    f'"q" int);'
                    # Создание индекса на поле "метка времени" ("ts")
                    f'CREATE INDEX "{tbl_name}_idx" ON public."{tbl_name}" '
                    f'USING btree ("x");')

                if tag.data.attributes.prsValueTypeCode == 4:
                    query += (f'CREATE INDEX "{tbl_name}_json__idx" ON public."{tbl_name}" '
                                'USING gin ("y" jsonb_path_ops);')


                await conn.execute(query)

    async def set_data(self, data: Dict):
        # data:
        # {
        #        "<tag_id>": [(x, y, q)]
        # }
        #

        async with self.conn_pool.acquire() as conn:
            for tag_id in data.keys():
                tag_cache = svc.get_tag_cache(tag_id, "data_storage")
                tag_tbl = tag_cache["table"]
                update = tag_cache["u"]
                data_items = data[tag_id]

                # для одного значения нет смысла тратить время
                # на PreparedStatement
                if len(data_items) <= 1:
                    q = ""
                    if update:
                        x, _, _ = data_items[0]
                        q = f'delete from "{tag_tbl}" where x = {x}; '
                    n = "NULL"
                    q += f'insert into "{tag_tbl}" (x, y, q) values ({data_items[0][0]}, {(n, data_items[0][1])[bool(data_items[0][1])]}, {(n, data_items[0][2])[bool(data_items[0][2])]})'

                    res = await conn.execute (q)
                else:
                    if update:
                        xs = [x for x, _, _ in data_items]
                        q = await conn.prepare(f"delete from {tag_tbl} where x in ({','.join(xs)})")
                        await q.execute(xs)

                    q = await conn.prepare(f"insert into {tag_tbl} (x, y, q) values ($1, $2, $3)")
                    res = await q.executemany(data_items)

            svc.logger.debug(res)

        return Response(status_code=204)

    async def _form_tag_cache(self, tag: PrsTagEntry) -> Dict:
        res = json.loads(tag.data.attributes.prsStore)
        res['u'] = tag.data.attributes.prsUpdate
        return res
