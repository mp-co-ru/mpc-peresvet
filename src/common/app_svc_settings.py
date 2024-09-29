"""
Класс, от которого наследуются все классы-настройки для сервисов.
Наследуется от класса ``pydantic.BaseSettings``\, все настройки передаются
в json-файлах либо в переменных окружения.
По умолчанию имя файла с настройками - ``config.json``\.
Имя конфигурационного файла передаётся сервису в переменной окружения
``config_file``\.
"""

from src.common.svc_settings import SvcSettings

class AppSvcSettings(SvcSettings):
   pass
