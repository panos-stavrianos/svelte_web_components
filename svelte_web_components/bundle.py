import glob
import json
import os
import shutil
import subprocess
import time
from re import sub
import filecmp

from jinja2 import FileSystemLoader, Environment

from svelte_web_components.setup_node import setup_node


def kebab(s):
    return '-'.join(
        sub(r"(\s|_|-)+", " ",
            sub(r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
                lambda mo: ' ' + mo.group(0).lower(), s)).split())


from svelte_web_components.paths import npm_path, node_path, get_path


def get_npm_ls():
    res = subprocess.check_output([npm_path(), "ls", "--json"])
    return json.loads(res)


def npm_install():
    if os.path.exists("./node_modules"):
        return None
    return subprocess.check_output([npm_path(), "install"])


def npm_install_extra(extra: list) -> str | None:
    if extra is None:
        return None
    packages = get_npm_ls()["dependencies"]
    for package in extra:
        if package not in packages:
            continue
        extra.remove(package)
    if len(extra) == 0:
        return None

    return subprocess.check_output([npm_path(), "install", *extra]).decode("utf-8")


def build_components_js():
    build_js = "build.mjs"
    return subprocess.check_output([node_path(), build_js]).decode("utf-8")


def generate_import_statements2(component_path, component_js):
    import_statements = []
    export_statements = []
    for svelte_file in glob.glob(os.path.join(component_path, '**/*.svelte'), recursive=True):
        relative_path = os.path.relpath(svelte_file, component_path)
        component_name = os.path.splitext(os.path.basename(svelte_file))[0]
        import_statement = f"import {component_name} from './components/{relative_path}';"
        import_statements.append(import_statement)

        export_statements.append(component_name)

    import_statements = "\n".join(import_statements)
    export_statement = "\nexport default [{" \
                       f" {', '.join(export_statements)} " \
                       "}]"

    with open(component_js, 'w') as js_file:
        js_file.write(import_statements + export_statement)


def generate_import_statements(component_path, component_js):
    packages = []

    for svelte_file in glob.glob(os.path.join(component_path, '**/*.svelte'), recursive=True):
        relative_path = os.path.relpath(svelte_file, component_path)
        component_name = os.path.splitext(os.path.basename(svelte_file))[0]

        package = {
            "name": component_name,
            "path": relative_path,
            "tag": kebab(component_name)
        }
        packages.append(package)
    environment = Environment(loader=FileSystemLoader(get_path("svelte_app")))
    template = environment.get_template("main.js.jinja2")
    rendered = template.render(packages=packages)

    with open(component_js, 'w+') as js_file:
        js_file.write(rendered)


def copy_components_path(components_path: str | os.PathLike):
    if os.path.exists(get_path("svelte_app/components")):
        shutil.rmtree(get_path("svelte_app/components"))
    shutil.copytree(components_path, get_path("svelte_app/components"))


def get_components_js(components_path: str | os.PathLike, extra_packages: list | None = None) -> str:
    components_path = os.path.abspath(components_path)
    current_path = os.getcwd()
    os.chdir(get_path("./svelte_app"))
    copy_components_path(components_path)
    # set env variables

    generate_import_statements(get_path("svelte_app/components"),
                               get_path("svelte_app/components.js"))

    npm_install_extra(extra_packages)
    res = build_components_js()
    os.chdir(current_path)
    return res


class Bundle:
    def __init__(self, components: dict[str, str | os.PathLike], extra_packages: list | None = None):
        self.components = components
        self.extra_packages = extra_packages
        self.bundled = {}
        setup_node()
        self.build()

    def build(self):
        for component_name, component_path in self.components.items():
            self.bundled[component_name] = get_components_js(component_path, self.extra_packages)

    def __getitem__(self, item):
        return self.bundled[item]


if __name__ == "__main__":
    # # overwrite the contents of the svelte_app folder
    # shutil.copytree("./svelte_app", get_path("svelte_app"), dirs_exist_ok=True)
    #
    # generate_import_statements("/home/panos/WebstormProjects/svelte_test/src/components",
    #                            "/home/panos/WebstormProjects/svelte_test/src/components.js")
    #
    # b = Bundle({"comp": "/home/panos/Downloads/comp"}, ["moment"])
    # print(b["comp"])
    shutil.copytree("/home/panos/Downloads/comp", get_path("svelte_app/components"), dirs_exist_ok=True)
    for i in range(100):
        s_time = time.time()
        print(filecmp.dircmp("/home/panos/Downloads/comp", get_path("svelte_app/components")).diff_files)
        print((time.time() - s_time) * 1000, "ms")
