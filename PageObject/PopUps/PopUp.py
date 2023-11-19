import datetime


class PopupType:
    """
    Словари с необходимыми селекторами и текстами для конструктора модальных окон
    """

    CREATE_OBJECT = {
        'popup_name': "New object",
        'MAIN_CONTAINER': ".modal-dialog",
        'HEADER': ".modal-header",
        'HEADER_TEXT': ".modal-title",
        'INPUT_FIELD': "input.form-control:nth-child(2)",
        'INPUT_FIELD_ERROR': ".errors-info",
        'INPUT_FIELD_DROPDOWN': "div.form-control > button:nth-child(1) > span:nth-child(1)",
        'LEFT_BTN': ".js-submit",
        'RIGHT_BTN': "button.btn:nth-child(2)",
        "CANCEL_BTN": ".modal-header > button:nth-child(1)"
    }

    WARNING = {
    }

    STANDARD_POPUP = {
    }


class PopUp:
    """
    Класс содержащий методы для модальных окон
    """
    __slots__ = [
        'popup_name',
        '__driver',
        'is_exist',
        'default_timeout',
        'MAIN_CONTAINER',
        'HEADER',
        'HEADER_TEXT',
        'INPUT_FIELD',
        'INPUT_FIELD_ERROR',
        'INPUT_FIELD_DROPDOWN',
        "LEFT_BTN",
        "RIGHT_BTN",
        "CANCEL_BTN",
    ]

    def __init__(self, driver, popup_type_data: dict):
        for key, value in popup_type_data.items():
            if key in self.__slots__:
                setattr(self, key, value)

        self.__driver = driver
        """:type WebDriver.WebDriver.WebDriver"""

        popup = self.__driver.find_element_by_css_selector(self.MAIN_CONTAINER)
        self.is_exist = True if popup else False

    def fill_input_field(self, name):
        """
        Метод для вставки имени в поле ввода текста
        :param: name: str: текстовое имя
        """
        input_field = self.__driver.find_element_by_css_selector(self.INPUT_FIELD)
        input_field.send_keys(name)
        assert not self.__driver.find_element_by_css_selector(self.INPUT_FIELD_ERROR), \
            f"{self.popup_name} не позволяет вставить полученное имя: {name} в поле ввода {self.INPUT_FIELD}"

    def left_btn_click(self):
        """
        Метод для нажатия левой нижней кнопки PopUp
        """
        self.__driver.find_element_by_css_selector(self.LEFT_BTN).click()

    def wait_popup_is_not_visible(self):
        """
        Метод ожидания исчезновения PopUp
        """
        timeout = getattr(self, self.default_timeout, 10)
        future = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=timeout)
        timeout //= 10
        while self.__driver.wait_for_element_to_disappear(self.MAIN_CONTAINER, timeout=timeout) is not True:
            if datetime.datetime.now(datetime.UTC) > future:
                raise AssertionError(f"PopUp `{self.popup_name}` не исчез за отведенные {timeout}0 секунд")
