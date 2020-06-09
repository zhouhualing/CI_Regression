import yaml
from framework.core import singleton
from framework.utils.path_helper import PathHelper


class YmlManager(object, metaclass=singleton.Singleton):
    def __init__(self, mode=None):
        super().__init__()
        self._mode = mode
        self._app = None
        self.load("application-dev.yml")

    def load(self, fn):
        if not ':' in fn:
            fn = PathHelper.join_path(PathHelper.get_project_path(), fn)
        with open(fn, 'r', encoding="utf-8") as f:
            self._app = yaml.load(f)
        return self._app


    @property
    def application(self):
        return self._app

    @property
    def getConfigGetAppKeyUrl(self):
        return self._app["secret.pkcs8"]


if __name__ == "__main__":
    print(YmlManager().application)
    ss = YmlManager().getConfigGetAppKeyUrl()
