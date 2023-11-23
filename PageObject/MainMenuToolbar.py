from abc import ABC

from PageObject import LoginScreen
from PageObject.BaseMethods import BaseMethods


class MainMenuToolbar(BaseMethods, ABC):
    """
    Класс, содержащий ключи локализации, селекторы и методы,
    используемые в верхней строке 'HeaderMenu' на главной странице SAYMON UI
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
    def __init__(self, driver):
        super().__init__(driver)
        self.__driver = driver
        """:type WebDriver.WebDriver.WebDriver"""
        self.SELECTORS = self.SELECTORS | dict(zip(self.LOCALES, self.LOCALES))

    def to_login_screen(self) -> LoginScreen:
        """
        Метод проброса WebDriver в другой PageObject
        :return:
        """
        return LoginScreen(self.__driver)

    def logout(self) -> None:
        """
        Метод выхода пользователя и завершения сессии
        """
        url = self.__driver.current_url.replace('/', '').split(':')[-1]
        if any(text in self.__driver.page_source for text in [url, 'care@saymon.info']):
            return
        logout = self.to_login_screen()
        if logout.check_page_title_exists(
            logout.locale[logout.SELECTORS['TEXT_TITLE_TAB_PAGE']], timeout=0.5, alert=False, message=' '
        ):
            return
        self.click_on_element(self.SELECTORS['TOGGLE_DROPDOWN_USER'])
        self.dropdown_item_select(self.SELECTORS['ITEM_USER_EXIT'])
        logout.check_page_title_exists(logout.locale[logout.SELECTORS['TEXT_TITLE_TAB_PAGE']])
