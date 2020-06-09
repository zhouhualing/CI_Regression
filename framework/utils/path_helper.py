import os


class PathHelper(object):
    PROJECT_PATH = None
    TEMP_FILE_PATH = None
    APP_DATA_PATH = None
    COOKIE_PATH = None

    @staticmethod
    def get_project_path():
        return PathHelper.PROJECT_PATH

    @staticmethod
    def get_temp_file_path():
        return PathHelper.TEMP_FILE_PATH

    @staticmethod
    def get_app_data_path():
        return PathHelper.APP_DATA_PATH

    @staticmethod
    def get_cookie_path():
        return PathHelper.COOKIE_PATH

