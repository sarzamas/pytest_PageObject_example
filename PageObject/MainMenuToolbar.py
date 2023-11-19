from abc import ABC

from Config import Config
from PageObject import LoginScreen
from PageObject.BaseMethods import BaseMethods


class MainMenuToolbar(BaseMethods, ABC):
    """
    Класс, содержащий селекторы и методы, используемые в верхней строке 'HeaderMenu' на главной странице SAYMON UI
    """
    # <editor-fold desc="CONSTANTS">
    LOCALES = [
        'TEXT_TITLE_TAB_PAGE',
    ]

    SELECTORS = {
        'BUTTON_OBJECT_CREATE': "#js-create-object",
        'BUTTON_DROPDOWN_OBJECT_CREATE': "#js-create-dropdown-toggle",

        'TOGGLE_DROPDOWN_USER': ".dropdown > button:nth-child(1)",

        'ITEM_OBJECT_CREATE': "ul.dropdown-menu:nth-child(7) > li:nth-child(1) > a:nth-child(1)",
        'ITEM_USER_CONFIG': "ul.dropdown-menu:nth-child(2) > li:nth-child(2) > a:nth-child(1)",
        'ITEM_USER_EXIT': "ul.dropdown-menu:nth-child(2) > li:nth-child(6) > a:nth-child(1)",
    }

    # </editor-fold desc="Constants">
    def __init__(self, driver, locale):
        super().__init__(driver)
        self.__driver = driver
        """:type WebDriver.WebDriver.WebDriver"""
        self.__locale = locale(Config.os_language)
        """:type Locales.Locale"""
        self.SELECTORS = self.SELECTORS | dict(zip(self.LOCALES, self.LOCALES))

    def to_login_screen(self):
        return LoginScreen(self.__driver, self.__locale)

    def logout(self):
        self.click_on_element(self.SELECTORS['TOGGLE_DROPDOWN_USER'])
        self.dropdown_item_select(self.SELECTORS['ITEM_USER_EXIT'])
        login_page = self.to_login_screen()
        assert login_page.verify_page_title_exists(login_page.SELECTORS['TEXT_TITLE_TAB_PAGE']), \
            "LogOut процедура неуспешна!"
