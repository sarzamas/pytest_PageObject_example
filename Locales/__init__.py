import json
import os

import yaml

from Config import Config
from PageObject.BaseMethods import BaseMethods
from Utils import LOCALES_PATH, lookup_report, read_locale_file
from Utils.DotDict import DotDict


class Locale(DotDict):
    """
    Класс данных локализации текстов PageObject в DotDict нотации
    - для хранения и синхронизации текстовок используются файлы .yaml для каждого языка
    - в каждом файле текстовки группируется по принадлежности к PageObject
    - при запуске производится считывание файла и проверка консистентности указателей в файле и в коде PageObject
    - в случае обнаружения отличий в указателях - генерируется подсказка какого указателя с текстом не хватает в файле
    - в случае консистентности указателей текстовки копируются в объекты PageObject и в файл _backup (отсортированными)
    """

    def __init__(self, lang: str, allow_tags=False):
        if allow_tags is not None:
            locale_data = read_locale_file(lang, allow_tags)
            super().__init__(DotDict(locale_data))

    def __write_locale(self) -> None:
        """
        Метод записывает содержимое locale, определяющей локализацию текущей сессии в JSON и YAML файлы
        """
        json_path = os.path.join(LOCALES_PATH, "locale_backup.json")
        yaml_path = os.path.join(LOCALES_PATH, "locale_backup.yaml")
        with open(json_path, 'w', encoding='UTF-8') as file:
            file.write(json.dumps(self, indent=4, sort_keys=True, ensure_ascii=False))
        with open(yaml_path, 'w', encoding='UTF-8') as file:
            file.write(yaml.dump(self, indent=4, sort_keys=True, allow_unicode=True, default_flow_style=False))

    def update_locale(self, lang: str) -> None:
        """
        Метод обновления locale в объектах PageObject
        """
        prefix = f"{os.linesep}{'*' * 145}{os.linesep}* В файле локализации " \
                 f"{os.path.relpath(os.path.join(LOCALES_PATH, lang, f'saymon_{lang}.yaml'))} "
        if len(self.items()) == 0:
            prefix = f"{prefix}отсутствуют данные или используется неизвестный tag: импорт данных заблокирован"
            print(prefix, end='')
            raise KeyError(prefix, lookup_report())

        page_objects = list(BaseMethods.get_all_subclasses())
        if not any(self.get(page.__name__) for page in page_objects):
            prefix = (f"{prefix}обнаружен  !tag:{os.linesep}*\tПри отсутствии флага разрешения использования тэгов в "
                      f"файле конфигурации {Config().config_path} - импорт данных локализации заблокирован "
                      f"{os.linesep}{'*' * 145}{os.linesep}*\t!!!ВНИМАНИЕ!!! - потенциальная уязвимость -\t"
                      f"Устанавливайте флаг разрешения тэгов только при доверии к источнику файлов локализации!")
            print(prefix, end='')
            raise KeyError(prefix, lookup_report())

        for page in page_objects:
            if page.LOCALES:
                for key in page.LOCALES:
                    if key not in self.get(page.__name__).keys():
                        prefix = (f"{prefix}отсутствует запись с локализацией для ключа `{key}`, "
                                  f"объявленного в PageObject `{page.__name__}`")
                        print(prefix)
                        raise KeyError(prefix, lookup_report())
            page.locale = self.get(page.__name__)

        print(f"OS Locale:\t{Config(update_file=True).os_language}{os.linesep}"
              f"UI Locale:\t{lang}{os.linesep * 2}{'*' * 80}")
        self.__write_locale()
