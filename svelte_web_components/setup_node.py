import os
import shutil
import tarfile

import requests

from svelte_web_components.bundle import npm_install
from svelte_web_components.paths import data_path, get_path, paths_init

paths_init()
print(data_path())
shutil.copytree("./svelte_app", get_path("svelte_app"))

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
npm_install()
