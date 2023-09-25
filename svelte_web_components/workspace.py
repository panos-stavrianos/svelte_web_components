import filecmp
import glob
import json
import os
import pathlib
import tarfile
import uuid
from re import sub

import requests
import sh
from dirhash import dirhash
from jinja2 import Environment, FileSystemLoader
from sh import mkdir, mv, cp, rm


def kebab(s):
    return '-'.join(
        sub(
            r"(\s|_|-)+",
            " ",
            sub(
                r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
                lambda mo: f' {mo.group(0).lower()}',
                s,
            ),
        ).split()
    )


class Workspace:
    home_path = os.path.expanduser('~')
    library_name = '.svelte_web_components'
    library_path = pathlib.Path(__file__).parent.resolve()
    library_data_path = os.path.join(library_path, "svelte_app")

    data_path = os.path.join(home_path, library_name)
    workspace_path = os.path.join(home_path, library_name, "workspace")
    projects_path = os.path.join(home_path, library_name, "workspace/projects")
    node_url = "https://nodejs.org/dist/v20.6.0/node-v20.6.0-linux-x64.tar.xz"

    node = None
    npx = None
    npm = None
    yarn = None
    yarn_workspace = None

    def __init__(self):
        self.init_commands()

    def init_commands(self):
        if not os.path.exists(self.data_path):
            self.setup_workspace()
        self.node = sh.Command(os.path.join(self.data_path, "node/bin/node"))
        self.npx = sh.Command(os.path.join(self.data_path, "node/bin/npx"))
        self.npm = sh.Command(os.path.join(self.data_path, "node/bin/npm"))
        self.yarn = self.npx.bake("yarn")
        self.yarn_workspace = self.yarn.bake("workspace")

    def _install_node(self):
        with requests.get(self.node_url, stream=True) as rx, tarfile.open(fileobj=rx.raw, mode="r|*") as tarobj:
            tarobj.extractall()

        # rename the extracted folder to 'node'
        mv("./node-v20.6.0-linux-x64", "./node")
        self.init_commands()

    def ls(self) -> list[str]:
        return os.listdir(self.projects_path)

    def add_package_json(self):
        if not os.path.exists("package.json"):
            cp(os.path.join(self.library_path, "svelte_app/package.json"), "package.json")

    def setup_workspace(self, clean=False):
        if clean and os.path.exists(os.path.join(self.home_path, self.library_name)):
            rm("-rf", os.path.join(self.home_path, self.library_name))
        with sh.pushd(self.home_path):  # ~
            mkdir("-p", self.library_name)
            with sh.pushd(self.library_name):  # ~/.svelte_web_components
                if not os.path.exists("node"):
                    self._install_node()
                mkdir("-p", "workspace")
                with sh.pushd("workspace"):  # ~/.svelte_web_components/self
                    if not os.path.exists("node_modules"):
                        self.npm("install", "yarn")
                        self.add_package_json()
                        print(self.yarn("install"))
                    mkdir("-p", "projects")

    def add_project(self, name):
        if name in self.ls():
            return
        with sh.pushd(self.projects_path):
            mkdir(name)
            with sh.pushd(name):
                cp(os.path.join(self.library_path, "svelte_app/vite.config.mjs"), "vite.config.mjs")
                with open(os.path.join(self.library_path, "svelte_app/project_package.json")) as package_file:
                    package_json = json.load(package_file)
                    package_json["name"] = name
                with open("package.json", 'w+') as package_file:
                    json.dump(package_json, package_file, indent=5)

        with sh.pushd(self.workspace_path):
            self.yarn_workspace(name, "install")

    def rm_project(self, name):
        if name not in self.ls():
            raise ValueError(f"Project {name} does not exist")
        with sh.pushd(self.projects_path):
            rm("-rf", name)

    def did_components_change(self, name, components_path):
        internal_path = os.path.join(self.projects_path, name, "components")
        if not os.path.exists(internal_path):
            return True
        diff_files = filecmp.dircmp(components_path, internal_path, ignore=["version.txt"]).diff_files
        return len(diff_files) > 0

    def set_components(self, name, components_path):
        internal_path = os.path.join(self.projects_path, name, "components")
        if not self.did_components_change(name, components_path):
            return
        if os.path.exists(internal_path):
            rm("-rf", internal_path)
        cp("-r", components_path, internal_path)

    def generate_components_js(self, name):
        components_path = os.path.join(self.projects_path, name, "components")
        packages = []
        for svelte_file in glob.glob(os.path.join(components_path, '**/*.svelte'), recursive=True):
            relative_path = os.path.relpath(svelte_file, components_path)
            component_name = os.path.splitext(os.path.basename(svelte_file))[0]

            package = {
                "name": component_name,
                "path": relative_path,
                "tag": kebab(component_name)
            }
            packages.append(package)
        environment = Environment(loader=FileSystemLoader(self.library_data_path))
        template = environment.get_template("main.js.jinja2")
        rendered = template.render(packages=packages)

        with open(os.path.join(self.projects_path, name, "components.js"), 'w+') as js_file:
            js_file.write(rendered)

    def components_directory_hash(self, name) -> str | None:
        components_path = os.path.join(self.projects_path, name, "components")
        if os.path.exists(components_path):
            return dirhash(components_path, "md5")
        return None

    def need_build(self, name):
        dist_version = os.path.join(self.projects_path, name, "dist/version.txt")
        components_version = os.path.join(self.projects_path, name, "components/version.txt")
        if os.path.exists(dist_version) and os.path.exists(components_version):
            with open(dist_version) as dist_file, open(components_version) as components_file:
                return dist_file.read() != components_file.read()
        return True

    def did_extra_packages_change(self, name, extra_packages):
        if not extra_packages:
            return False
        package_json_path = os.path.join(self.projects_path, name, "package.json")
        if not os.path.exists(package_json_path):
            return True
        with open(package_json_path) as package_file:
            package_json = json.load(package_file)
            if "dependencies" not in package_json:
                return True
            for package, version in extra_packages.items():
                if package not in package_json["dependencies"]:
                    return True
                if package_json["dependencies"][package] != version:
                    return True
        return False

    def build(self, name, extra_packages=None, output_path=None):
        extra_packages_changed = self.did_extra_packages_change(name, extra_packages)
        if not self.need_build(name) and not extra_packages_changed:
            print("No need to build")
            self.copy_to_output(name, output_path)
            return
        if extra_packages_changed:
            self.add_extra_packages(name, extra_packages)
        self.generate_components_js(name)
        with sh.pushd(self.projects_path):
            self.yarn_workspace(name, "run", "build")

        dist_version = os.path.join(self.projects_path, name, "dist/version.txt")
        components_version = os.path.join(self.projects_path, name, "components/version.txt")

        # random uid
        current_version = str(uuid.uuid4())
        print("Current version:", current_version)
        with open(dist_version, 'w+') as dist_file, open(components_version, 'w+') as components_file:
            dist_file.write(current_version)
            components_file.write(current_version)

    def copy_to_output(self, name, output_path=None):
        if output_path:
            with sh.pushd(self.projects_path):
                mkdir("-p", output_path)
                cp(self.components_js_path(name), os.path.join(output_path, f"{name}.js"))

    def components_js_path(self, name):
        return os.path.join(self.projects_path, name, "dist/components.js")

    def components_js(self, name):
        with open(self.components_js_path(name)) as js_file:
            return js_file.read()

    def add_extra_packages(self, name: str, extra_packages: str | list[str] | dict[str, str] | None):
        with open(os.path.join(self.projects_path, name, "package.json")) as package_file:
            package_json = json.load(package_file)
            if "dependencies" not in package_json:
                package_json["dependencies"] = {}

            for package, version in extra_packages.items():
                package_json["dependencies"][package] = version

        with open(os.path.join(self.projects_path, name, "package.json"), 'w+') as package_file:
            json.dump(package_json, package_file, indent=5)

        with sh.pushd(self.workspace_path):
            print(self.yarn_workspace(name, "install"))

    def clean(self):
        # TODO: clean
        pass

    def remote_build(self, config: dict):
        # TODO: remote build
        pass
