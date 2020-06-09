import yaml
from framework.core import singleton
import os

from framework.utils import path_helper


class YmlManager(object, metaclass=singleton.Singleton):
    def __init__(self, mode=None):
        super().__init__()
        self._mode = mode
        self._app= None
        self.load()

    def load(self):
        pass


    @property
    def application(self):
        return self._app


if __name__ == "__main__":
    print(YmlManager().application)
    print(YmlManager().application)