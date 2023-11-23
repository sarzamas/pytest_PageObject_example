import os
from datetime import datetime
from uuid import uuid4

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

from Config import Config
from WebDriver.WebBase import WebBase


def log_file_path(log_path):
    log_name = datetime.now().strftime('%Y-%m-%d_T_%H_%M_%S') + ".log"

    if not log_path:
        base_logs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Logs")
        os.mkdir(base_logs_path) if not os.path.exists(base_logs_path) else None
        log_path = os.path.join(base_logs_path, log_name)
    else:
        log_path = os.path.join(log_path, log_name)

    return log_path


class WebDriver(WebBase):
    """
    Класс инициализирующий WebDriver с требуемыми параметрами
    """

    def __init__(self, config: Config, name: str = None):
        """:type name: selenium.webdriver.WebDriver"""
        super().__init__()
        self.config = config
        self.name = config.browser.selenoid.executor_id.format(name) if config.browser.selenoid.executor_id else None
        self.driver = (
            self.__local_driver_init()
            if not self.config.browser.selenoid.use_selenoid
            else self.__remote_driver_init(name)
        )

    def __getattr__(self, item):
        return getattr(self.driver, item)

    def __local_driver_init(self) -> webdriver.Chrome | webdriver.Firefox:
        """
        Создает локальный экземпляр WebDriver для управления браузером
        """
        config = self.config.browser
        browser = config.browser_name

        if browser == 'firefox':
            path = config.firefox.driver_path or 'geckodriver'
            log_path = log_file_path(config.firefox.log_path)
            options = FirefoxOptions()
            if config.firefox.binary_path:
                options.binary_location = config.firefox.binary_path
            if config.headless:
                options.add_argument("--headless")

            profile = webdriver.FirefoxProfile()
            profile.accept_untrusted_certs = True
            profile.set_preference("app.update.auto", False)
            profile.set_preference("app.update.enabled", False)
            profile.update_preferences()

            service = FirefoxService(executable_path=path, log_output=log_path)
            driver = webdriver.Firefox(service=service, options=options)

        elif browser == 'chrome':
            path = config.chrome.driver_path or 'chromedriver'
            log_path = log_file_path(config.chrome.log_path)
            options = ChromeOptions()
            if config.chrome.binary_path:
                options.binary_location = config.chrome.binary_path
            if config.headless:
                options.add_argument("--headless=new")

            service = ChromeService(executable_path=path, log_output=log_path)
            driver = webdriver.Chrome(service=service, options=options)

        if config.window.maximize:
            driver.maximize_window()
        else:
            driver.set_window_size(config.window.size.width, config.window.size.height)

        return driver

    def __remote_driver_init(self, name) -> webdriver.Remote:
        """
        Создает удаленный экземпляр webdriver (в selenoid) для управления браузером
        """
        config = self.config.browser
        if config.browser_name == 'firefox':
            options = webdriver.FirefoxOptions()
            options.headless = config.headless
            capabilities = options.to_capabilities()
            capabilities['sessionTimeout'] = "5m"
            name = (
                f"Браузер зарезервирован {config.selenoid.executor_id} для теста: "
                f"{name if name else config.selenoid.executor_id + ' ' + str(uuid4())}"
            )
            capabilities['name'] = name
            capabilities['pageLoadStrategy'] = "eager"
            capabilities['acceptSslCerts'] = True
            capabilities['enableVNC'] = True
            capabilities['version'] = "72.0"
            driver = webdriver.Remote(command_executor=config.selenoid_url, desired_capabilities=capabilities)

            if config.window.maximize:
                driver.maximize_window()
            else:
                driver.set_window_size(config.window.size.width, config.window.size.height)
            return driver

        raise NotImplementedError("Браузер не поддерживается")

    def open_page(self, url):
        """
        Метод для проверки загрузки страницы полностью
        """
        try:
            self.driver.get(url)
            self.wait_interactive_ready_state()
        except Exception as e:
            raise TimeoutError(f"Страница {url} не загрузилась!") from e
