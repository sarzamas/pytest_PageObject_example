import os
from time import sleep

from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchWindowException,
    TimeoutException,
    UnexpectedAlertPresentException,
    WebDriverException,
)
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

TIMEOUT_STEP = 0.5
MAX_TIMEOUT = 5


class WebBase:
    """type: selenium.webdriver.remote.webelement.WebElement"""

    def __init__(self):
        self.driver = None
        self.elem = None

    def __custom_find_by(self, by_method: str, value: str, timeout: float | int, wait_element_visibility=True):
        """
        Кастомная обертка методов поиска WebElement с поддержкой таймаутов и поиска невидимых элементов
        """
        from WebDriver.WebElement import WebElement  # isort:skip

        driver = self.driver if not isinstance(self, WebElement) else self.elem

        if not isinstance(self, WebElement):
            self.wait_interactive_ready_state()

        def _expected_condition(_driver):
            """
            Функция поиска для метода until
            :param _driver: экземпляр WebDriver
            :return: первый найденный WbElement или NoSuchElementException
            """
            prop = getattr(_driver, 'find_elements')

            # Получаем список элементов
            elems = prop(by_method, value)

            # Если элементов не нашлось, падаем и пробуем снова пока работает until
            if not elems:
                raise NoSuchElementException

            for el in elems:
                if el.is_displayed():
                    return el

                if wait_element_visibility is False:
                    return el

            raise NoSuchElementException

        wait = WebDriverWait(
            driver,
            timeout,
            TIMEOUT_STEP,
            ignored_exceptions=[
                NoSuchElementException,
            ],
        )

        try:
            return WebElement(
                wait.until(
                    _expected_condition,
                    message=f"INFO:\tНа странице с PageTitle: `{driver.title}` WebElement с селектором `{value}`"
                    f" не найден за {timeout} сек",
                ),
                driver,
            )

        except TimeoutException as e:
            print(str(e))
            return None

    def __custom_finds_by(self, by_method: str, value: str, timeout: float | int, wait_element_visibility=True):
        """
        Кастомная обертка методов поиска WebElements с поддержкой таймаутов и поиска невидимых элементов
        """
        from WebDriver.WebElement import WebElement  # isort:skip

        driver = self.driver if not isinstance(self, WebElement) else self.elem

        if not isinstance(self, WebElement):
            self.wait_interactive_ready_state()

        def _expected_condition(_driver):
            """
            Функция поиска для метода until
            :param _driver: экземпляр WebDriver
            :return: список найденных WbElement или NoSuchElementException
            """
            result = []
            prop = getattr(_driver, 'find_elements')
            elems = prop(by_method, value)

            if not elems:
                raise NoSuchElementException

            for el in elems:
                if el.is_displayed():
                    result.append(el)
                    continue

                if wait_element_visibility is False:
                    result.append(el)
                    continue

                if not result:
                    raise NoSuchElementException

            return result

        wait = WebDriverWait(
            driver,
            timeout,
            TIMEOUT_STEP,
            ignored_exceptions=[
                NoSuchElementException,
            ],
        )

        try:
            ret_results = []
            elements = wait.until(
                _expected_condition,
                message=f"INFO:\tНа странице с PageTitle: `{driver.title}` WebElement с селектором `{value}` "
                f"не найден за {timeout} сек",
            )
            for element in elements:
                ret_results.append(WebElement(element, driver))
            return ret_results
        except TimeoutException as e:
            print(str(e))
            return []

    def wait_interactive_ready_state(self):
        """
        Ждет пока у страницы document.readyState станет interactive
        """

        def _interactive_ready_state(driver):
            sleep(TIMEOUT_STEP)
            ready_state = driver.execute_script("return document.readyState")
            return bool(any(["interactive", "complete"]) in ready_state)

        try:
            WebDriverWait(self.driver, timeout=MAX_TIMEOUT).until(
                _interactive_ready_state,
                message=f"ERROR:\tСтраница с PageTitle: `{self.driver.title}` "
                f"не загрузилась за {MAX_TIMEOUT} сек{os.linesep}",
            )

        except (NoSuchWindowException, UnexpectedAlertPresentException, WebDriverException, TypeError):
            return

    def find_element_by_css_selector(self, value, timeout=MAX_TIMEOUT, wait_element_visibility=True):
        return self.__custom_find_by(By.CSS_SELECTOR, value, timeout, wait_element_visibility)

    def find_elements_by_css_selector(self, value, timeout=MAX_TIMEOUT, wait_element_visibility=True):
        return self.__custom_finds_by(By.CSS_SELECTOR, value, timeout, wait_element_visibility)

    def find_element_by_xpath(self, value, timeout=MAX_TIMEOUT, wait_element_visibility=True):
        return self.__custom_find_by(By.XPATH, value, timeout, wait_element_visibility)

    def find_elements_by_xpath(self, value, timeout=MAX_TIMEOUT, wait_element_visibility=True):
        return self.__custom_finds_by(By.XPATH, value, timeout, wait_element_visibility)

    def find_element_by_link_text(self, value, timeout=MAX_TIMEOUT, wait_element_visibility=True):
        """
        Метод поиска элемента по текстовой ссылке (href#)
        Поиск по всем элементам страницы возвращает первый удовлетворяющий критерию элемент
        :param value: текст ссылки по которому надо найти элемент
        :param timeout: максимальное время ожидания появления элемента
        :param wait_element_visibility: признак видимости элемента
        :return: WebElement или None
        """
        return self.__custom_find_by('find_elements_by_link_text', value, timeout, wait_element_visibility)

    def wait_for_element_to_disappear(self, selector, timeout=MAX_TIMEOUT):
        """
        Ждать, когда элемент с указанным селектором исчезнет
        Ошибки ожидания метод не генерит!
        :param selector: Селектор элемента
        :param timeout: максимальное время ожидания исчезновения элемента
        :return: bool: True - элемент исчез, False - нет
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                ec.invisibility_of_element_located((By.CSS_SELECTOR, selector)),
                message=f"WebElement с селектором: `{selector}` не исчез за {timeout} секунд",
            )
        except TimeoutException as e:
            print(str(e))
            return False
        return True

    def find_element_in_table_by_text(
        self, table_items, text, match_case=False, match_words=False, timeout=MAX_TIMEOUT, check_elements=True
    ):
        """
        Ищет указанный текст во всех элементах таблицы и возвращает первый элемент в котором был найден текст
        :param table_items: селектор списка элементов таблицы
        :param text: текст для поиска
        :param match_case: учитывать регистр текста
        :param match_words: учитывать полное совпадение по словам
        :param int timeout: сколько секунд нужно ждать появления таблицы
        :param check_elements: нужна ли проверка найденных элементов таблицы по селектору
        :return: WebElement или None
        """
        elements = self.find_elements_by_css_selector(table_items, timeout)
        if check_elements:
            assert elements, f"Не найдены элементы таблицы по селектору `{table_items}`"

        for el in elements:
            el_text = el.text if match_case else el.text.lower()
            text = text if match_case else text.lower()
            if match_words and text == el_text:
                return el
            if not match_words and text in el_text:
                return el

        return None

    def move_to_element(self, element=None):
        """
        Навести курсор на указанный элемент. Если элемент не указан, то попытается навести на тот элемент у которого
        был вызван данный метод
        """
        if not element:
            if not self.elem:
                raise TypeError("Не передан элемент для наведения курсора")
            element = self
        if isinstance(element, list):
            element = element[0]
        actions = ActionChains(self.driver).move_to_element(element.elem)
        actions.perform()
        return element
