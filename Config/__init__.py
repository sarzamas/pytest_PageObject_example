import json
import os

from Utils import os_locale, read_file
from Utils.DotDict import DotDict


class Config(DotDict):
    """Класс конфигурационных данных в DotDict нотации"""

    def __init__(self, update_file=False) -> None:
        config_dir = os.path.dirname(os.path.abspath(__file__))
        self.__config_path = os.path.join(config_dir, 'config.json')
        local_config_path = os.path.join(config_dir, 'config.local.json')
        if os.path.exists(local_config_path):
            self.__config_path = local_config_path
        config_data = read_file(self.__config_path, 'json')
        super().__init__(DotDict(config_data))
        if update_file:
            self.locale.os_locale = os_locale()
            self.__rewrite_config()

    @property
    def config_path(self) -> str:
        """
        Свойство возвращает относительный путь до используемого файла конфигурации
        :return: str:
        """
        return os.path.relpath(self.__config_path)

    @property
    def saymon_admin_user(self) -> DotDict:
        """
        Свойство возвращает словарь с учетными данными Администратора на WEB UI SAYMON
        :return: dict: DotDict
        """
        return self.saymon.users.admin_user

    @property
    def os_language(self) -> str:
        """
        Свойство возвращает значение языка WEB UI SAYMON
        :return: str:
        """
        return self.locale.os_locale

    @os_language.setter
    def os_language(self, value: str) -> None:
        self.locale.os_locale = value

    @property
    def allow_yaml_tags(self) -> bool:
        """
        Свойство возвращает разрешение на использование tags в yaml файлах
        :return: str:
        """
        return self.locale.allow_yaml_tags

    def __rewrite_config(self) -> None:
        """
        Метод перезаписывает содержимое конфига в json файл определяющий конфиг
        """
        with open(self.__config_path, 'w', encoding='UTF-8') as file:
            file.write(json.dumps(self, indent=4, sort_keys=True))
