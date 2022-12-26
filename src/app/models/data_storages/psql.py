import json
import copy
from typing import Dict

from fastapi import HTTPException, Response

import asyncpg as apg

from app.models.DataStorage import PrsDataStorageEntry
from app.models.Tag import PrsTagEntry
from app.svc.Services import Services as svc
from app.const import CNHTTPExceptionCodes as HEC

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

    def __await__(self, **kwargs):
        super(PrsPostgreSQLEntry, self).__await__()
        self.conn_pool = apg.create_pool(dsn=self.dsn).__await__()

    def _format_data_store(self, tag: PrsTagEntry) -> None | Dict:
        if not tag.data.attributes.prsStore:
            return {
                'table': f"t_{tag.id}",
                'u': tag.data.attributes.prsUpdate # флаг обновления значения
            }

        try:
            _ = json.loads(tag.data.attributes.prsStore)["table"]
        except json.JSONDecodeError as _:
            svc.logger.error((
                f"Для тега id:{tag.id}, dn={tag.dn} неверный формат атрибута `smtStore`. "
                "Формат атрибута: {'table': '<table_name>'}"
            ))
            return

        return tag.data.attributes.prsStore

    async def connect(self) -> int:
        return 0

    async def create_tag_store(self, tag: PrsTagEntry):

        tbl_name = tag.data.attributes.prsStore['table']

        s_type = None
        match tag.data.attributes.prsValueTypeCode:
            case 1:
                s_type = "bigint"
            case 2:
                s_type = "double precision"
            case 3:
                s_type = "text"
            case 4:
                s_type = "jsonb"
            case _:
                svc.logger.error(f"Тег: {tag.id}; неизвестный тип данных: {tag.data.attributes.prsValueTypeCode}")
                raise HTTPException(HEC.CN_500, f"Тег: {tag.id}; неизвестный тип данных: {tag.data.attributes.prsValueTypeCode}")
    # -------------------------------------------------------------------------

        # Запрос на создание таблицы в РСУБД
        query = (f'CREATE TABLE public."{tbl_name}" ('
            '"id" serial primary key,'
            '"x" bigint NOT NULL,'
            '"y" {s_type},'
            '"q" int);'
            # Создание индекса на поле "метка времени" ("ts")
            'CREATE INDEX "{tbl_name}_idx" ON public."{tbl_name}" '
            'USING btree ("x");')

        if tag.data.attributes.prsValueTypeCode == 4:
            query += (f'CREATE INDEX "{tbl_name}_json__idx" ON public."{tbl_name}" '
                        'USING gin ("y" jsonb_path_ops);')

        with self.conn_pool.acquire() as conn:
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
                        q = f"delete from {tag_tbl} where x = {x};"
                    q += f"insert into {tag_tbl} (x, y, q) values ({data_items[0][0], data_items[0][1], data_items[0][2]})"

                    await conn.execute (q)
                else:
                    if update:
                        xs = [x for x, _, _ in data_items]
                        q = await conn.prepare(f"delete from {tag_tbl} where x = $1")
                        await q.executemany(xs)

                    q = await conn.prepare(f"insert into {tag_tbl} (x, y, q) values ($1, $2, $3)")
                    await q.executemany(data_items)

        return Response(status_code=204)
