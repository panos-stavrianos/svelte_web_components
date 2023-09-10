import os
import pathlib
import shutil
from pathlib import Path

project_name = ".svelte_web_components"


def paths_init():
    if os.path.exists(data_path()):
        shutil.rmtree(data_path())
    os.mkdir(data_path())


def data_path():
    return os.path.join(str(Path.home()), project_name)


def lib_path(path):
    p = pathlib.Path(__file__).parent.resolve()
    return os.path.join(p, path)


def get_path(path):
    return os.path.join(data_path(), path)


def npm_path():
    return os.path.join(data_path(), "node/bin/npm")


def node_path():
    return os.path.join(data_path(), "node/bin/node")
