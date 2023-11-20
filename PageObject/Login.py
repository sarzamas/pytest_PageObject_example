from abc import ABC

from PageObject.BaseMethods import BaseMethods
from Utils.DotDict import DotDict


class LoginScreen(BaseMethods, ABC):
    """
    Класс, содержащий ключи локализации, селекторы и методы, используемые на странице авторизации
    """
    # <editor-fold desc="CONSTANTS">
    LOCALES = [
        'TEXT_ERROR_LOGIN_INVALID',  # (3) Неверный логин или пароль #  TODO почему счетчик не изменяется у admin?
        'TEXT_ITEM_LANG_RUSSIAN',  # русский
        'TEXT_TITLE_ERROR_LABEL',  # Ошибка!
        'TEXT_TITLE_POPUP_LOGIN',  # Вход в систему
        'TEXT_TITLE_POPUP_NEW_PSW',  # Новый пароль
        'TEXT_TITLE_TAB_PAGE',  # Loading...
        'TEXT_TITLE_WARNING',  # Предупреждение:
        'TEXT_WARNING_PASSWORD_NEW',  # Необходимо изменить пароль
        'TEXT_WARNING_PSW_MISMATCH',  # Пароли не совпадают
    ]

    SELECTORS = {
        'TITLE_POPUP_LOGIN': ".modal-title",
        'TITLE_ERROR_LABEL': ".alert > strong",

        'MESSAGE_ERROR_LOGIN_INVALID': ".msg",
        'MESSAGE_WARNING_PSW_MISMATCH': ".control-label",

        'HOOVER_LANGUAGE': ".filter-option > span:nth-child(2)",

        'INPUT_FIELD_LOGIN': "#user-login",
        'INPUT_FIELD_PASSWORD': "#user-password",
        'INPUT_FIELD_NEW_PSW': "div.col-md-12:nth-child(1) > input:nth-child(1)",
        'INPUT_FIELD_CONFIRM_PSW': "div.col-md-12:nth-child(2) > input:nth-child(1)",

        'BUTTON_LOGIN': ".js-submit > span:nth-child(1)",
        'BUTTON_SAVE': ".btn-primary",
        'BUTTON_CANCEL': ".close",

        'TOGGLE_DROPDOWN_LANG': ".dropdown-toggle",

        'ITEM_LANG_ENGLISH': ".flag-us",
        'ITEM_LANG_ITALIAN': ".flag-it",
        'ITEM_LANG_RUSSIAN': ".flag-ru",

        'LOADING_DOTS': "div.bounce"
    }

    # </editor-fold desc="Constants">
    def __init__(self, driver) -> None:
        super().__init__(driver)
        self.SELECTORS = self.SELECTORS | dict(zip(self.LOCALES, self.LOCALES))

    def set_ui_language(self, language: str) -> None:
        """
        Метод смены языка интерфейса в SAYMON UI
        :param language: str: язык интерфейса SAYMON UI
        """
        loading = self.find_element(self.SELECTORS['LOADING_DOTS'], timeout=0.5)
        self.wait_until_element_disappeared(self.SELECTORS['LOADING_DOTS'], timeout=60) if loading else None
        self.verify_element_availability(self.SELECTORS['TOGGLE_DROPDOWN_LANG'], enabled=True)
        self.click_on_element(self.SELECTORS['TOGGLE_DROPDOWN_LANG'])
        selector_name = None
        for key, value in {'ru': "RUSSIAN", 'en': "ENGLISH", 'it': "ITALIAN"}.items():
            if key == language:
                selector_name = f"ITEM_LANG_{value}"
                break
        if not selector_name:
            raise NotImplementedError(f"Локализация для языка `{language}` не реализована")

        self.click_on_element(self.SELECTORS[selector_name])

    def login(self, user: DotDict) -> None:
        """
        Метод обеспечивает тестовую сессию от имени администратора на WEB портале SAYMON UI
        preconditions:
        - Осуществляет `ВХОД` в SAYMON UI как администратор с учетными данными из config.json
        """
        self.check_page_title_exists(self.locale[self.SELECTORS['TEXT_TITLE_TAB_PAGE']])
        self.check_element_label_text(self.SELECTORS['TITLE_POPUP_LOGIN'],
                                      self.locale[self.SELECTORS['TEXT_TITLE_POPUP_LOGIN']])
        self.fill_text_input_field(self.SELECTORS['INPUT_FIELD_LOGIN'], user.login)
        self.fill_text_input_field(self.SELECTORS['INPUT_FIELD_PASSWORD'], user.password)
        self.click_on_element(self.SELECTORS['BUTTON_LOGIN'])
        if self.check_page_title_exists(
                self.locale[self.SELECTORS['TEXT_TITLE_TAB_PAGE']], timeout=0.5, delay=0.5, message=' ', alert=False):
            self.new_installation_setup(user.password)

    def new_installation_setup(self, password: str) -> None:
        """
        Метод смены пароля пользователя `admin` в SAYMON UI при новой установке SAYMON Server
        - начальное условие: на странице авторизации имеется ошибка `Invalid login or password`
        :param password: str: новый пароль (из файла config)
        """
        self.check_element_label_text(self.SELECTORS['TITLE_ERROR_LABEL'],
                                      self.locale[self.SELECTORS['TEXT_TITLE_ERROR_LABEL']])
        self.check_element_label_text(self.SELECTORS['MESSAGE_ERROR_LOGIN_INVALID'],
                                      self.locale[self.SELECTORS['TEXT_ERROR_LOGIN_INVALID']])
        self.click_on_element(self.SELECTORS['BUTTON_CANCEL'])
        self.fill_text_input_field(self.SELECTORS['INPUT_FIELD_PASSWORD'], "saymon")
        self.click_on_element(self.SELECTORS['BUTTON_LOGIN'])
        self.check_element_label_text(self.SELECTORS['TITLE_POPUP_LOGIN'],
                                      self.locale[self.SELECTORS['TEXT_TITLE_POPUP_NEW_PSW']])
        self.check_element_label_text(self.SELECTORS['TITLE_ERROR_LABEL'],
                                      f"{self.locale[self.SELECTORS['TEXT_TITLE_WARNING']]}")
        self.check_element_label_text(self.SELECTORS['MESSAGE_ERROR_LOGIN_INVALID'],
                                      self.locale[self.SELECTORS['TEXT_WARNING_PASSWORD_NEW']])
        self.fill_text_input_field(self.SELECTORS['INPUT_FIELD_NEW_PSW'], password)
        self.fill_text_input_field(self.SELECTORS['INPUT_FIELD_CONFIRM_PSW'], ' ')
        self.verify_element_availability(self.SELECTORS['BUTTON_SAVE'], disabled=True)
        self.check_element_label_text(self.SELECTORS['MESSAGE_WARNING_PSW_MISMATCH'],
                                      self.locale[self.SELECTORS['TEXT_WARNING_PSW_MISMATCH']])
        self.fill_text_input_field(self.SELECTORS['INPUT_FIELD_CONFIRM_PSW'], password, typing_speed_delay=False)
        self.verify_element_availability(self.SELECTORS['BUTTON_SAVE'], enabled=True)
        self.click_on_element(self.SELECTORS['BUTTON_SAVE'])
