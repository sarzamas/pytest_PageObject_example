from PageObject.Login import LoginScreen
from PageObject.MainMenuToolbar import MainMenuToolbar


class PageObject:
    """
    Класс реализующий паттерн PageObject
    """

    def __init__(self, driver, locale):
        self.__login_screen = LoginScreen(driver, locale)
        self.__main_menu_toolbar = MainMenuToolbar(driver, locale)

    @property
    def login_screen(self) -> LoginScreen:
        return self.__login_screen

    @property
    def main_menu_toolbar(self) -> MainMenuToolbar:
        return self.__main_menu_toolbar
