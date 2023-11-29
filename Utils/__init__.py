import ctypes
import inspect
import json
import locale
from os import curdir, getenv, linesep, listdir, name, path, remove, rmdir
from typing import Optional

import yaml

PROJECT_PATH = path.split(path.dirname(__file__))[0]
TMP_PATH = path.join(PROJECT_PATH, 'share')
LOCALES_PATH = path.join(PROJECT_PATH, 'Locales')
for _ in (TMP_PATH,):
    pass  # mkdir(_) if not path.exists(_) else None


def get_props(class_name) -> list:
    """
    Функция возвращает список @property у класса
    :param class_name: str: имя класса
    :return: props_list: list: список @property
    """
    props_list = [prop for prop in dir(class_name) if isinstance(getattr(class_name, prop), property)]
    return props_list


def os_locale() -> str:
    """
    Функция определения языка и типа ОС
    :return: lang: str
    """
    if name == 'posix':
        lang = getenv('LANG')[:2]
    elif name == 'windows':
        windll = ctypes.windll.kernel32
        lang = locale.windows_locale[windll.GetUserDefaultUILanguage()][:2]
    else:
        raise NotImplementedError("Неизвестная ОС")
    print(f"{linesep}{'*' * 80}{linesep * 2}OS type:\t{name}")
    return lang


def read_locale_file(lang: property | str, allow_tags: Optional[property | bool] = None) -> dict:
    """
    Функция проверки наличия и чтения файла локализации
    :param lang: str: язык интерфейса SAYMON UI
    :param allow_tags: bool: запрет/разрешение наличия tags в yaml файле (потенциальная уязвимость)
    :return: locale_data: dict:
    """
    if any(isinstance(param, property) for param in [lang, allow_tags]):
        locale_data = {}
    else:
        locale_file_path = None
        file_name = f"saymon_{lang}"
        for ext in ['yml', 'yaml']:
            if path.exists(path.join(LOCALES_PATH, lang, f"{file_name}.{ext}")):
                file_name = f"{file_name}.{ext}"
                locale_file_path = path.join(LOCALES_PATH, lang, file_name)
        if locale_file_path:
            locale_data = read_file(locale_file_path, 'yaml', yaml_tags=allow_tags)
        else:
            prefix = (
                f"{linesep}\t* Отсутствует файл локализации текстов для языка `{lang}`{linesep}\t* "
                f"Поместите файл `{file_name}.yaml` по следующему пути в проекте: "
                f"{path.relpath(path.join(LOCALES_PATH, lang, f'{file_name}.yaml'), start=curdir)}"
            )
            print(prefix)
            raise FileNotFoundError(prefix, lookup_report())
    return locale_data


def read_file(file_path: str, decoder: str, yaml_tags: Optional[bool] = None) -> dict:
    """
    Функция чтения данных их файла в словарь
    :param file_path: str: путь к файлу на диске
    :param decoder: тип декодера (расширение файла)
    :param yaml_tags: bool: запрет/разрешение наличия tags в yaml файле (потенциальная уязвимость)
    :return: dict: data словарь с данными из файла
    """
    with open(file_path, "rt", encoding="utf-8") as file:
        if decoder == 'yaml':
            loader = yaml.Loader if yaml_tags else yaml.BaseLoader
            data = yaml.load(file, Loader=loader)
        elif decoder == 'json':
            data = json.load(file)
        else:
            raise NotImplementedError(f"Декодер `{decoder}` не реализован!")
    return data


def remove_local_dir(dir_path: str | bytes) -> None:
    """
    Функция рекурсивного удаления директории на локальном хосте
        - если путь к директории существует, то директория удаляется с содержимым
        - если такой путь не существует, ошибка не генерируется
    :param dir_path: абсолютный путь к директории
    """
    if path.exists(dir_path):
        lsdir = listdir(dir_path)

        if not lsdir:
            rmdir(dir_path)
            return

        for elem in lsdir:
            abs_path = path.join(dir_path, elem)
            try:
                remove(abs_path)  # remove file
            except (IsADirectoryError, PermissionError):
                remove_local_dir(abs_path)  # recursive call

        rmdir(dir_path)  # remove directory


def lookup_report() -> str:
    """
    Функция сбора метрик вызываемого и вызывающего методов с помощью inspect
    Ex: frame, filename, line_number, function_name, lines, index = inspect.stack()[<stack_frame_depth>]
    :return: str: данные о методе, из которого был вызван текущий метод
    """
    stack_frame_depth = (
        2
        if (
            inspect.stack()[1][3] == 'alert'
            or 'lookup_report()' in inspect.stack()[1][4][0]
            or 'raise' in inspect.stack()[1][4][0]
        )
        else 1
    )
    trace_source = {
        'called': inspect.stack()[stack_frame_depth],
        'caller': inspect.stack()[stack_frame_depth + 1],
        'caller-1': inspect.stack()[stack_frame_depth + 2],
        'caller-2': inspect.stack()[stack_frame_depth + 3],
    }
    lookup = {}
    for item, source in trace_source.items():
        lookup[item + '_name'] = source[3]
        lookup[item + '_file_path'] = path.relpath(source[1], start=curdir)
        lookup[item + '_line_nbr'] = source[2]
        lookup[item + '_line_text'] = source[4][0]

    report = (
        f"{linesep}{' ! ДАННЫЕ ОБ ОШИБКЕ ! ':*^145}{linesep}"
        f"* Вызываемый (Current Method):{'\t' * 3}`{lookup['called_name']}`\tв\t{lookup['called_file_path']}:"
        f"{lookup['called_line_nbr']}{linesep}*\tСтрока с ошибкой:\t{lookup['called_line_nbr']}"
        f"{lookup['called_line_text']}{'*' * 145}{linesep}"
        f"* Вызывающий (Caller Method):{'\t' * 3}`{lookup['caller_name']}`\tиз\t{lookup['caller_file_path']}:"
        f"{lookup['caller_line_nbr']}{linesep}*\t Строка вызова:{'\t' * 2}{lookup['caller_line_nbr']}"
        f"{lookup['caller_line_text']}{'*' * 145}{linesep}"
        f"* Вызывающий-1 (Predecessor Method):\t`{lookup['caller-1_name']}`\tиз\t{lookup['caller-1_file_path']}:"
        f"{lookup['caller-1_line_nbr']}{linesep}*\t Строка вызова:{'\t' * 2}{lookup['caller-1_line_nbr']}"
        f"{lookup['caller-1_line_text']}{'*' * 145}{linesep}"
        f"* Вызывающий-2 (Forerunner Method):\t\t`{lookup['caller-2_name']}`\tиз\t{lookup['caller-2_file_path']}:"
        f"{lookup['caller-2_line_nbr']}{linesep}*\t Строка вызова:{'\t' * 2}{lookup['caller-2_line_nbr']}"
        f"{lookup['caller-2_line_text']}{'*' * 145}{linesep}"
    )

    print(report, end='')
    return report
