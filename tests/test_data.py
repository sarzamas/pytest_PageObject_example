import pytest
pytestmark = [pytest.mark.saymon_ui, pytest.mark.data]


class TestData:
    """
    Секция: Данные
    Чек-лист: https://sitechco.saymon.info/project/2/checklist/2570/details
    Language: {"RUSSIAN": 'ru', "ENGLISH": 'en', "ITALIAN": 'it'}
    """
    LANGUAGE = ['ru', 'en', 'it']

    @pytest.fixture(scope='function', name='locale_ru')
    def preconditions_teardown_ru(self, test_data):
        """
        Фикстура подготовки и очищения окружения для тестов данного класса
        :param test_data: базовая фикстура подготовки и очищения окружения
        :return: параметризованный результат выполнения базовой фикстуры
        """
        return test_data(self.LANGUAGE[0])

    @pytest.fixture(scope='function', name='locale_en')
    def preconditions_teardown_en(self, test_data):
        """
        Фикстура подготовки и очищения окружения для тестов данного класса
        :param test_data: базовая фикстура подготовки и очищения окружения
        :return: параметризованный результат выполнения базовой фикстуры
        """
        return test_data(self.LANGUAGE[1])

    @pytest.mark.ru
    def test_strict_values_ru(self, locale_ru):
        """
        Тест округления точных значений
        """
        pass

    @pytest.mark.en
    def test_strict_values_en(self, locale_en):
        """
        Тест округления точных значений
        """
        pass
