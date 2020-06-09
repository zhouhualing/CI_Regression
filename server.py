#!/usr/bin/python3

import os
import sys

from framework.config.yml_manager import YmlManager


def init_path_helper():
    from framework.utils import path_helper
    path_helper.PathHelper.PROJECT_PATH = os.path.abspath(
        os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])))).replace('\\', '/')
    path_helper.PathHelper.APP_DATA_PATH = os.path.join(
        path_helper.PathHelper.get_project_path(),"data").replace('\\', '/')
    path_helper.PathHelper.TEMP_FILE_PATH = os.path.join(
        path_helper.PathHelper.get_project_path(), "tmp").replace('\\', '/')


if __name__ == '__main__':
    init_path_helper()
    YmlManager().load()
