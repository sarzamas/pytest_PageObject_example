import pytest

from Config import Config
from Locales import Locale
from PageObject import PageObject
from WebDriver.WebDriver import WebDriver


@pytest.fixture(scope='function', name='test_data')
def preconditions_teardown(config, driver, locale, page_object):
    """
    Фикстура выполняет следующие действия для подготовки и очищения тестового окружения:
    preconditions:
        - Осуществляет `ВХОД` в SAYMON UI как администратор
        - Изменяет язык интерфейса на требуемый в тесте
        - Обновляет пароль (при первом входе)
        - Валидирует переход в основной интерфейс SAYMON UI
    teardown:
        - Валидирует `ВЫХОД` из SAYMON UI
    """

    def _preconditions_teardown(language):
        locale(language).update_locale(language)
        driver.open_page(config.browser.base_url)
        login = page_object.login_screen
        login.set_ui_language(language)
        login.login(config.saymon_admin_user)

    return _preconditions_teardown


@pytest.fixture(scope='session')
def config():
    """
    Фикстура инициализации Config
    :return: DotDict: словарь с конфигурационными данными
    """
    config = Config()

    return config


@pytest.fixture(scope='class')
def locale():
    """
    Фикстура инициализации Locale (локализация текстов)
    :return: DotDict: словарь с локализованными текстами
    """

    def _locale(lang):
        allow_tags = None if isinstance(lang, property) else Config().allow_yaml_tags
        locale = Locale(lang, allow_tags=allow_tags)
        return locale

    return _locale


@pytest.fixture(scope='class')
def driver(config):
    """ Фикстура инициализации и закрытия WebDriver """
    webdriver = WebDriver(config)

    yield webdriver

    webdriver.quit()


@pytest.fixture(scope='class')
def page_object(driver, locale):
    """ Фикстура инициализации PageObject """

    return PageObject(driver, locale)
