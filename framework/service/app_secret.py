from framework.config.yml_manager import YmlManager
from framework.core import singleton


class SecretManager(object, metaclass=singleton):
    def getAppkey(self):
        url = YmlManager().application.getConfigGetAppKeyUrl();

