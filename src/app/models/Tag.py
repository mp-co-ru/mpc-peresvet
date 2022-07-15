from pydantic import Field
from ldap3 import DEREF_ALWAYS, LEVEL

from app.svc.Services import Services as svc
from app.models.ModelNode import PrsModelNodeCreateAttrs, PrsModelNodeCreate, PrsModelNodeEntry

class PrsTagCreateAttrs(PrsModelNodeCreateAttrs):
    """Attributes for request for /tags/ POST"""

    """top"""
    prsValueTypeCode: int = Field(1, title='Тип значения тэга',
        description=(
            '- 1 - целое\n'
            '- 2 - вещественное\n'
            '- 3 - строка\n'
            '- 4 - json\n'
        )
    )
    prsSource: str = Field(None, title='`id` источника данных',
        description=(
            'В случае, если тэг получает данные из внешнего источника данных, в этом атрибуте содержится `id` этого источника данных. '
            'При подключении к **Пересвету** источник данных получает список всех тэгов, в которые он должен записывать данные.'
        )
    )
    prsStore: str = Field(None, title='Способ хранения данных в хранилище',
        description=(
            'Атрибут описывает, как найти данные тэга в хранилище. '
            'К примеру, для реляционной базы данных - это имя таблицы. '
            'Для Victoriametrics - метрика и список тэгов. '
            'Если параметр не указан, то хранилище самостоятельно создаёт '
            '"место" для вновь создаваемого тэга. '
            'Если параметр указан, то: если указанное "место" уже существует, '
            'то просто привязывается к тэгу, если же не существует, то '
            'будет создано.'
        )
    )
    prsMeasureUnits: str = Field(None, title='Единицы измерения тэга')
    prsMaxDev: float = Field(0, title='Максимальное отклонение',
        description=(
            'Отклонение от предыдущего значения тэга, при превышении которого источник данных отправляет значение в **Пересвет**. '
            'К примеру, в тэг записывается температура, `prsMaxDev = 0.5` и предыдущее записанное в тэг значение - 21ºС. '
            'В таком случае, если последующие считывания значения температуры с датчика лежат в пределах (20.5, 21.5), '
            'то они будут проигнорированы.'
        )
    )
    prsMaxLineDev: float = Field(0, title='Максимальное линейное отклонение',
        description=(
            'Параметр, влияющий на фильтрацию значений тэгов, только уже не на уровне источника данных, как в случае с `prsMaxDev`, '
            'а на уровне ядра.'
        )
    )
    prsArchive: bool = Field(True, title='Флаг хранения истории значений тэга',
        description=(
            'Если = `False`, то храниться будет только текущее значение тэга.'
        )
    )
    prsCompress: bool = Field(True, title='Флаг сжатия данных',
        description=(
            'Если = `True`, то будет задействован алгоритм сжатия данных тэга (флаг `prsMaxLineDev`), '
            'иначе в хранилище будет записано каждое новое пришедшее значение тэга.'
        )
    )
    prsValueScale: float = Field(1, title='Коээфициент, на который умножается значение тэга.',
        description=(
            'Перед отправкой значения тэга в **Пересвет** коннектор умножает его на этот коэффициент.'
        )
    )
    prsStep: bool = Field(False, title='Флаг применения линейной интерполяции к значениям тэга')
    prsUpdate: bool = Field(True, title='Флаг обновлений значений тэга',
        description=(
            '`True`: если новое значение тэга приходит с меткой времени, которая уже есть в хранилище, то новое значение переписывает старое. '
            'В противном случае в хранилище будут записаны оба значения.'
        )
    )
    prsDefaultValue: str = Field(None, title='Значение тэга по умолчанию',
        description='Если задано, то это значение тэга будет записано в хранилище при создании тэга.'
    )

class PrsTagCreate(PrsModelNodeCreate):
    """Request /tags/ POST"""
    connectorId: str = Field(None, title='Id коннектора, являющегося поставщиком данных для тэга.', description='По умолчанию отсутствует.')
    dataStorageId: str = Field(None, title='Id хранилища данных.', description='В случае отсутствия берётся хранилище по умолчанию.')
    attributes: PrsTagCreateAttrs = PrsTagCreateAttrs()

class PrsTagEntry(PrsModelNodeEntry):
    payload_class = PrsTagCreate
    objectClass: str = 'prsTag'
    default_parent_dn: str = svc.config["LDAP_TAGS_NODE"]

    def _add_subnodes(self) -> None:
        super()._add_subnodes()

        system_node = PrsModelNodeCreate()
        system_node.attributes.cn = 'system'
        system_node.parentId = self.id
        node_entry = PrsModelNodeEntry(data=system_node)
        if self.data.dataStorageId is not None:
            svc.ldap.add_alias(node_entry.dn, svc.data_storages[self.data.dataStorageId].dn, "dataStorage")
        if self.data.connectorId is not None:
            # исправление ошибки circular import
            from app.models.Connector import PrsConnectorEntry
            conn = PrsConnectorEntry(id=self.data.connectorId)
            svc.ldap.add_alias(node_entry.dn, conn.dn, "connector")

    def _load_subnodes(self):
        found, _, response, _ = svc.ldap.get_read_conn().search(
            search_base=f"cn=system,{self.dn}",
            search_filter='(objectClass=prsDataStorage)', search_scope=LEVEL, dereference_aliases=DEREF_ALWAYS,
            attributes=['entryUUID'])
        if found:
            self.data.dataStorageId = str(response[0]['attributes']['entryUUID'])

        found, _, response, _ = svc.ldap.get_read_conn().search(
            search_base=f"cn=system,{self.dn}",
            search_filter='(objectClass=prsConnector)', search_scope=LEVEL, dereference_aliases=DEREF_ALWAYS,
            attributes=['entryUUID'])
        if found:
            self.data.connectorId = str(response[0]['attributes']['entryUUID'])
