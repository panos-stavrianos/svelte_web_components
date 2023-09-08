import glob
import json
import os
import shutil
import subprocess

from appdata import AppDataPaths

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
    res = subprocess.check_output([node_path(), build_js]).decode("utf-8")
    return res


def generate_import_statements(component_path, component_js):
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


def copy_components_path(components_path: str | os.PathLike):
    shutil.copytree(components_path, get_path("./svelte_app/components"))


def get_components_js(components_path: str | os.PathLike, extra_packages: list | None = None) -> str:
    app_paths = AppDataPaths()

    os.chdir(get_path("./svelte_app"))
    copy_components_path(components_path)
    # set env variables

    generate_import_statements(get_path("./svelte_app/components"),
                               get_path("./svelte_app/components.js"))

    npm_install_extra(extra_packages)
    res = build_components_js()
    print(len(res))
    return res


if __name__ == "__main__":
    # generate_import_statements("/home/panos/Downloads/comp", "/home/panos/Downloads/comp/components.js")
    get_components_js("/home/panos/Downloads/comp", ["moment"])
