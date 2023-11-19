import random
from time import sleep

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

from WebDriver.WebBase import WebBase


class WebElement(WebBase):

    def __init__(self, element: SeleniumWebElement, driver):
        super().__init__()
        self.elem = element
        self.driver = driver
        """:type WebDriver.WebDriver.WebDriver"""

    def __getattr__(self, item):
        return getattr(self.elem, item)

    def fill(self, text, clear=True, typing_speed_delay=None, min_delay=0.05, max_delay=0.25):
        """
        Ввести в текстовое поле значение
        """
        self.elem.click()

        if clear:
            self.elem.clear()
            self.clear()

        if typing_speed_delay:
            for character in list(text):
                sleep(typing_speed_delay) \
                    if isinstance(typing_speed_delay, int) \
                    else sleep(random.uniform(min_delay, max_delay))
                self.elem.send_keys(character)
            return self

        self.elem.send_keys(text)

        return self

    def clear(self):
        """
        Принудительно очистить поле
        """
        self.elem.send_keys(Keys.CONTROL + "a")
        self.elem.send_keys(Keys.DELETE)

    def verify_text(self, text):
        """
        Сравнить текст указанного элемента с ожидаемым
        """
        element = self.elem
        assert element, "Не найден ожидаемый элемент."
        text = str(text)
        real_text = str(element.text)
        assert text == real_text, "Текст элемента не соответствует ожидаемому. " \
                                  "Ожидаемый текст: %s Имеющийся текст: %s" % (text, real_text)
        return self

    def verify_value(self, value, timeout=5):
        """
        Сравнить value указанного элемента с ожидаемым
        """
        element = self.elem
        assert element, "Не найден ожидаемый элемент."
        value = str(value)
        real_value = None
        for i in range(timeout):
            real_value = str(element.get_attribute('value'))
        if value == real_value:
            return self
        assert value == real_value, "value элемента не соответствует ожидаемому. " \
                                    "Ожидаемый value: %s Имеющийся value: %s" % (value, real_value)
        return self

    def is_disabled(self) -> bool:
        """
        Проверить:
         - наличие атрибута элемента 'disabled'
         - атрибут элемента `class` на наличие класса с текстом 'disabled'
        :return: bool
        """
        return True if self.elem.get_attribute("disabled") or 'disabled' in self.elem.get_attribute("class") else False
