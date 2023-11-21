# pytest_PageObject_example
Пример реализации паттерна PageObject с помощью Pytest 

## Установка:
- клонировать проект, реализовать python3.12 venv
- установить зависимости из файла `requirements.txt`
```code
$ pip install -r requirements.txt
```
- скачать дистрибутивы webdriver (chrome/gecko), распаковать архивы и разместить файлы в папке `/usr/local/bin/`
```code
$ cd ~/Downloads
$ sudo mv chromedriver /usr/local/bin
$ sudo mv geckodriver /usr/local/bin
```
- из шаблона `config.json` создать локальный файл `config.local.json` (файл в .gitignore)
- указать в локальном файле конфигурации следующие значения:
-- url сервера в формате `'http://<IP ADDRESS>'`
-- имя браузера: `chrome` / `firefox`
-- путь до соответствующего webdriver `driver_path`
-- новый пароль для пользователя `admin`
