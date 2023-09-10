import os
import shutil
import tarfile

import requests

from svelte_web_components.paths import data_path, get_path, paths_init, lib_path


def check_setup():
    if os.path.exists(get_path("svelte_app")):
        return True
    return False


def setup_node(force=False):
    if not force and check_setup():
        print("Node already setup")
        return None

    if os.path.exists(data_path()):
        shutil.rmtree(data_path())

    paths_init()
    print("setup_node", data_path())
    shutil.copytree(lib_path("svelte_app"), get_path("svelte_app"))

    current_path = os.getcwd()
    os.chdir(data_path())

    # copy the svelte app to the app data path

    if os.path.exists("./node"):
        shutil.rmtree("./node")
    url = "https://nodejs.org/dist/v20.6.0/node-v20.6.0-linux-x64.tar.xz"
    with requests.get(url, stream=True) as rx, tarfile.open(fileobj=rx.raw, mode="r|*") as tarobj:
        tarobj.extractall()

    # rename the extracted folder to 'node'
    os.rename("./node-v20.6.0-linux-x64", "./node")
    os.chdir("./svelte_app")
    from svelte_web_components.bundle import npm_install

    npm_install()

    os.chdir(current_path)
