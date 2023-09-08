import os
import shutil
import tarfile

import requests
from appdata import AppDataPaths

from svelte_web_components.bundle import npm_install

app_paths = AppDataPaths()
app_paths.clear(everything=True)
app_paths.setup()

data_path = app_paths.app_data_path
print(data_path)
shutil.copytree("./svelte_app", os.path.join(data_path, "svelte_app"))

os.chdir(data_path)

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
