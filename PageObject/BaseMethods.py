import os
from abc import abstractmethod
from time import sleep
from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

import WebDriver.WebDriver

import Locales
from Utils import lookup_report
from Utils.DotDict import DotDict


class BaseMethods:
    """
    Класс, содержащий методы, используемые на всех страницах PageObject
    """
    # <editor-fold desc="CONSTANTS">
    MAX_WAIT_TIME = 15
    SELECTORS: dict

    # </editor-fold desc="Constants">

    def __new__(cls, *args, **kwargs):
        if cls is BaseMethods:
            raise TypeError(f"@AbstractClass `{cls.__name__}` не предусматривает создание экземпляра")
        return object.__new__(cls)

    def __init__(self, driver):
        self.__driver = driver
        """:type WebDriver.WebDriver.WebDriver"""
        self.__locale = None
        """:type Locales.Locale"""

    @classmethod
    def get_all_subclasses(cls) -> iter:
        """
        Генератор получения подклассов, унаследованных от данного класса
        :return: iter: генератор инстанциированных объектов, унаследованных от данного класса
        """
        for subclass in cls.__subclasses__():
            yield from subclass.get_all_subclasses()
            yield subclass

    @property
    @abstractmethod
    def locale(self) -> DotDict:
        """
        Свойство возвращает словарь с текстами элементов для данной страницы на выбранном языке
        :return: dict: DotDict
        """
        return self.__locale.get(self.__class__.__name__)

    @locale.setter
    @abstractmethod
    def locale(self, value: DotDict):
        self.__locale = value

    def get_name(self, val: str) -> str:
        """
        Метод поиска имени ключа в словаре по его значению
        :param val: str: значение ключа в словаре селекторов класса
        :return: key: str: имя ключа
        """
        prefix = (f"{os.linesep}{' ! ОШИБКА В СЕЛЕКТОРЕ ! ':*^145}"
                  f"{os.linesep}* PageObject `{self.__class__.__name__}`: ")
        if not isinstance(val, str):
            raise TypeError(f"{prefix}При вызове метода задано значение `{val}` для поиска имени селектора в словаре: "
                            f"{os.linesep}* {self.SELECTORS.items()}{lookup_report()}")
        if self.locale:
            for key, value in dict(self.SELECTORS | self.locale).items():
                if val == value:
                    return key
        else:
            raise FileExistsError(
                f"{os.linesep}Файл локализации для требуемого тестом языка `{os.path.relpath(Locales.LOCALES_PATH)}"
                f"/<language>/saymon_<language>.yml` пуст, проверьте содержимое файла!{lookup_report()}"
            )
        raise KeyError(f"{prefix}Ключ для значения `{val}` отсутствует в словаре {self.SELECTORS}{lookup_report()}")

    def alert(self, **kwargs: dict | str | int | bool) -> str:
        """
        Метод формирования текста сообщения об ошибке при поиске WebElement на странице и оценки его атрибутов
        :param kwargs: dict: ограниченный набор ключевых слов для составления фразы
        :return: alert: str: фраза с детализацией по ошибке
        """
        page = self.__class__.__name__
        prefix1 = prefix2 = ''
        params = {
            'name': "",
            'param': "",
            'enabled': "",
            'disabled': "",
            'timeout': "",
        }

        for key, value in kwargs.items():
            if key == 'name':
                params['name'] = value
            elif key == 'text':
                params['param'] = key
                prefix1 = "c текстом"
                prefix2 = "-\tне найден"
            elif key == 'selector':
                params['param'] = key
                prefix1 = "c селектором"
                prefix2 = "-\tне найден"
            elif key == 'disabled':
                if value:
                    prefix2 = f"{prefix2} в статусе `disabled`: True"
            elif key == 'enabled':
                if value:
                    prefix2 = f"{prefix2} в статусе `enabled`: True"
            elif key == 'timeout':
                prefix2 = f"-\tне исчез за {value} секунд"
            else:
                raise NameError(
                    f"{os.linesep}{' ! ОШИБКА В ПАРАМЕТРЕ ! ':*^145}{os.linesep}* PageObject `{page}`: "
                    f"Проверьте имена параметров в {kwargs.keys()} - какой-то из них не предусмотрен для обработки "
                    f"вызываемым методом{lookup_report()}"
                )

        return (f"{os.linesep}{' ! ОШИБКА В ЛОКАТОРЕ ! ':*^145}{os.linesep}* PageObject `{page}` по адресу "
                f"{self.__driver.current_url}{os.linesep}*\tWebElement:\t`{params['name']}`\t"
                f"{prefix1}:\t`{kwargs[params['param']]}`\t{prefix2} !{lookup_report()}")

    def find_element(self, selector: str, timeout=MAX_WAIT_TIME) -> Optional[WebDriver.WebDriver.WebDriver]:
        """
        Метод поиска WebElement в DOM по css-селектору
        :param selector: str: значение селектора для выполнения действия
        :param timeout: таймер ожидания
        :return: WebElement or None
        """
        element = self.__driver.find_element_by_css_selector(selector, timeout=timeout)

        return element

    def click_on_element(self, selector: str) -> None:
        """
        Метод для клика по элементу
        :param selector: str: значение селектора для выполнения действия
        """
        selector_name = self.get_name(selector)

        element = self.__driver.find_element_by_css_selector(selector)

        assert element, self.alert(name=selector_name, selector=selector)
        element.click()

    def fill_text_input_field(self, selector: str, text: str, clear=True, typing_speed_delay=None) -> None:
        """
        Метод заполнения поля ввода текстом
        :param selector: str: значение селектора для выполнения действия
        :param text: str: текст для ввода
        :param clear: bool: очистить поле перед вводом
        :param typing_speed_delay: None | int | str | bool
            - None: ввод текста блоком
            - int/float: ввод текста посимвольно с заданной фиксированной задержкой в секундах
            - str/bool: ввод текста посимвольно с переменной задержкой (см. метод:fill)
        """
        selector_name: str = self.get_name(selector)

        input_field = self.__driver.find_element_by_css_selector(selector)

        assert input_field, self.alert(name=selector_name, selector=selector)
        input_field.fill(text, clear=clear, typing_speed_delay=typing_speed_delay)

    def check_element_label_text(self, selector: str, text: str) -> WebDriver:
        """
        Метод проверки текста в наименовании элемента
        :param selector: str: значение селектора для выполнения действия
        :param text: str: текст для проверки
        """
        selector_name = self.get_name(selector)
        text_name = self.get_name(text)

        self.wait_for_element_is_visible(selector_name=selector_name, selector_value=selector)
        element = self.__driver.find_element_by_css_selector(selector)

        assert element, self.alert(name=selector_name, selector=selector)
        assert element.text == text, self.alert(name=text_name, text=text)

        return element

    def dropdown_item_select(self, item_selector: str) -> None:
        """
        Метод выбора пункта из выпадающего списка 'DropdownList' по селектору
        :param item_selector: str: значение селектора пункта для выбора
        :return: WebDriver: WebDriver: Переход в `LoginScreen` | `PopUp`
        """
        selector_name: str = self.get_name(item_selector)

        item = self.__driver.find_element_by_css_selector(item_selector)

        assert item, self.alert(name=selector_name, selector=item_selector)
        item.click()

    def wait_for_tooltip_is_visible(self, tooltip_selector: str, element_selector_to_show_tooltip=None,
                                    element_to_show_tooltip=None, timeout=MAX_WAIT_TIME, move_to_element=True) -> str:
        """
        Ждать появления подсказки, подождать закрытия, вернуть её текст
        :return: tooltip_text: str
        """
        tooltip_selector_name: str = self.get_name(tooltip_selector)
        if move_to_element:
            if element_selector_to_show_tooltip:
                element_to_show_tooltip = self.__driver.find_elements_by_css_selector(element_selector_to_show_tooltip)
            self.__driver.move_to_element(element_to_show_tooltip)
        tooltip_text = self.wait_for_element_is_visible(selector_name=tooltip_selector_name, timeout=timeout).text
        self.click_outside_of_element(element_to_show_tooltip)
        self.wait_for_element_is_not_visible(tooltip_selector)

        return tooltip_text

    def click_outside_of_element(self, element=None, selector_value=None) -> None:
        """
        Кликнуть вне элемента
        """
        actions = ActionChains(self.__driver)
        if not element:
            element = self.__driver.find_element_by_css_selector(selector_value)
        actions.move_to_element(element.elem)
        actions.move_by_offset((element.rect['width'] / 2 + 10) * -1, 0).perform()
        actions.click().perform()

    def wait_for_element_is_visible(self, element=None, selector_name=None, selector_value=None, obj=None,
                                    timeout=MAX_WAIT_TIME) -> WebDriver:
        """
        Ждать, когда указанный элемент станет видимым на странице
        :return: element: WebElement !!! АКТУАЛЬНЫЙ ТОЛЬКО ДО СЛЕДУЮЩЕГО ДЕЙСТВИЯ C DOM !!!
                                     После следующего действия element: становится `stale`
        """
        selector_name = self.get_name(selector_value) if not selector_name else selector_name
        selector_value = self.SELECTORS[selector_name] if not selector_value else selector_value
        driver = obj if obj else self.__driver
        if not element:
            element = driver.find_element_by_css_selector(selector_value, timeout=timeout)
        assert element, self.alert(name=selector_name, selector=selector_value)

        return element

    def wait_for_element_is_not_visible(self, element=None, element_selector=None, element_name=None, obj=None,
                                        timeout=MAX_WAIT_TIME) -> None:
        """
        Ждать, когда указанный элемент станет невидимым на странице
        """
        driver = obj if obj else self.__driver
        if not element:
            element = driver.wait_for_element_to_disappear(element_selector, timeout=timeout)

        assert element, ("Элемент: '{0}' остался видимым на странице".format
                         (element_name if element_name else element_selector))

    def wait_until_element_disappeared(self, selector: str, timeout=MAX_WAIT_TIME) -> bool:
        """
        Метод проверки, что WebElement, существующий на странице исчезнет за определенное время
        :param selector: str: значение селектора для выполнения действия
        :param timeout: int: ограничение времени ожидания
        :return: result:
            - True: - требование удовлетворено - bool:
            - AssertionError: - требование не удовлетворено
        """
        selector_name: str = self.get_name(selector)
        element = self.__driver.find_element_by_css_selector(selector, timeout=timeout)

        result = WebDriverWait(self.__driver, timeout).until(
            ec.staleness_of(element), message=self.alert(name=selector_name, selector=selector, timeout=timeout))
        return result

    def select_checkbox_by_text(self, label_selector: str, checkbox_selector: str, text: str) -> None:
        """
        Найти чекбокс по имени и выбрать его
        :param label_selector: str: значение селектора поля с текстом
        :param checkbox_selector: str: значение селектора чек-бокса
        :param text: str: значение поисковой фразы
        """
        items = self.__driver.find_elements_by_css_selector(label_selector)
        checkboxes = self.__driver.find_elements_by_css_selector(checkbox_selector)
        for item, checkbox in zip(items, checkboxes):
            if text in item.text:
                checkbox.click()

    def check_page_title_exists(self, contains_text: str, timeout=MAX_WAIT_TIME, delay: Optional[int | float] = None,
                                alert: bool = True) -> bool:
        """
        Метод проверки `PageTitle` заголовка закладки страницы браузера на `ContainsText`
         (или ждать его появления по `Timeout`)
        :param contains_text: str: значение поисковой фразы
        :param timeout: int | float: время ожидания появления заголовка (сек)
        :param delay: int | float: интервал времени до начала проверки (сек)
        :param alert: bool: вызывать/не вызывать AssertionError при отсутствии совпадения
        :return: result: bool или AssertionError
        """
        text_name = self.get_name(contains_text)
        result = False
        sleep(delay) if delay else None

        try:
            result = WebDriverWait(self.__driver, timeout).until(
                ec.title_contains(contains_text),
                message=f"INFO:\tОжидание страницы по адресу {self.__driver.current_url} с PageTitle: `{contains_text}`"
                        f" превысило отведенное время: {timeout} сек")
        except TimeoutException as e:
            print(str(e))
        if alert:
            assert result, self.alert(name=text_name, text=contains_text)

        return result

    def verify_element_availability(self, selector: str, enabled=False, disabled=False) -> bool:
        """
        Метод проверки WebElement на возможность с ним взаимодействовать:
         - проверяется наличие атрибута элемента 'disabled'
         - проверяется атрибут элемента class на наличие класса с текстом 'disabled'
        :param selector: str: значение селектора для выполнения действия
        :param enabled: bool: правило валидации:
            - True: ожидается что WebElement ~ enabled? иначе alert
        :param disabled: bool: правило валидации:
            - True: ожидается что WebElement ~ disabled? иначе alert
        :return: result:
            - True:  - правило удовлетворено - bool:
            - AssertionError: - правило не удовлетворено
        """
        selector_name: str = self.get_name(selector)
        element = self.__driver.find_element_by_css_selector(selector)
        assert element, self.alert(name=selector_name, selector=selector)

        result: Optional[bool] = None
        if all([enabled, disabled]) or all([not enabled, not disabled]):
            raise LookupError(
                f"{os.linesep}* PageObject: `{self.__class__.__name__}`: "
                f"Вызываемый метод предусматривает обязательное наличие на входе ОДНОГО и только ОДНОГО правила "
                f"валидации.{os.linesep}* Получено же в параметрах вызова: (enabled={enabled}, disabled={disabled})"
                f"{lookup_report()}"
            )
        if enabled:
            result = not element.is_disabled()
        elif disabled:
            result = element.is_disabled()
        assert result, self.alert(name=selector_name, selector=selector, enabled=enabled, disabled=disabled)
        return result
