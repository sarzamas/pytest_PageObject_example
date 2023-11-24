import os

from Utils import lookup_report


class DotDict(dict):
    """Using dot "." notation to access dictionary keys in Python"""

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, ddict):
        super().__init__()
        if isinstance(ddict, dict):
            for key, value in ddict.items():
                if hasattr(value, 'keys'):
                    value = DotDict(value)
                self[key] = value
        else:
            prefix = (
                f"{os.linesep}{'*' * 145}{os.linesep}* На входе Инициализатора класса DotDict: '{ddict}':\t"
                f"Проверьте содержимое источника данных (файла)"
            )
            print(prefix, end='')
            raise TypeError(f"{prefix}{lookup_report()})")
