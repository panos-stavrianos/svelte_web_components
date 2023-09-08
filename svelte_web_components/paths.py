import os
import shutil

from appdata import AppDataPaths

project_name = "svelte_web_components"

app_paths = AppDataPaths()


def paths_init():
    app_paths.setup()

    if os.path.exists(data_path()):
        shutil.rmtree(data_path())
    os.mkdir(data_path())


def data_path():
    app_paths.setup()
    data_path = os.path.join(app_paths.app_data_path, project_name)
    return data_path


def get_path(path):
    return os.path.join(data_path(), path)


def npm_path():
    return os.path.join(data_path(), "node/bin/npm")


def node_path():
    return os.path.join(data_path(), "node/bin/node")
