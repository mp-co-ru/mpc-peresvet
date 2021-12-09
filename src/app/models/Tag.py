from pydantic import BaseModel, validator, Field
from typing import List, Optional, Union

from app.svc.Services import Services as svc
from app.models.ModelNode import PrsModelNodeAttrs, PrsModelNodeCreate, PrsModelNodeEntry

class PrsTagCreateAttrs(PrsModelNodeAttrs):
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
    prsStore: str = Field(None, title='`id` хранилища данных',
        description=(
            '`id` хранилища данных, в котором должны содержаться данные тэга. '
            'В случае отсутствия используется хранилище по умолчанию.'
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
    parentId: str = None
    dataSourceId: str = None
    attributes: PrsTagCreateAttrs = PrsTagCreateAttrs()

class PrsTagEntry(PrsModelNodeEntry):
    payload_class = PrsTagCreate
    objectClass: str = 'prsTag'
    default_parent_dn: str = "cn=tags,{}".format(svc.config["LDAP_BASE_NODE"])
    
    
    