# pytest_PageObject_example [![linter](https://github.com/sarzamas/pytest_PageObject_example/actions/workflows/linter.yaml/badge.svg?branch=main&event=push)](https://github.com/sarzamas/pytest_PageObject_example/actions/workflows/linter.yaml)
Пример реализации паттерна PageObject с помощью Pytest
## Установка:
- Установить Python3.12, Chrome/Firefox
- Клонировать проект, реализовать python3.12 venv
- Установить зависимости из файла `requirements.txt`
```code
$ pip install -r requirements.txt
```
- Скачать дистрибутивы webdriver (chrome/gecko), распаковать архивы и разместить файлы в папке `/usr/local/bin/`
```code
$ cd ~/Downloads
$ sudo mv chromedriver /usr/local/bin
$ sudo mv geckodriver /usr/local/bin
```
- Из шаблона `config.json` создать локальный файл `config.local.json` (файл в .gitignore)
- Указать в локальном файле конфигурации следующие значения:

-- url сервера в формате `'http://<IP ADDRESS>'`

-- имя браузера: `chrome` / `firefox`

-- путь до соответствующего webdriver `driver_path`

-- новый пароль для пользователя `admin`

## Запуск:
- Запустить тесты в `terminal console` (CI/CD workflow)
```code
$ cd <ProjectPath>
$ python -m pytest
```
- Запустить тесты в `PyCharm`

> [!NOTE]
> Возможные проблемы при запуске `firefox` из `PyCharm` установленного через `snap`:
> - https://github.com/mozilla/geckodriver/issues/2062
