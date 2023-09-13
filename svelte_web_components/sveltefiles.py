import pathlib
import typing

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from svelte_web_components.bundle import Bundle

PathLike = typing.Union[str, "os.PathLike[str]"]


class SvelteFiles:
    def __init__(self, bundles: Bundle | list[Bundle], extra_packages: list | None = None,
                 app: FastAPI = None,
                 templates=None):
        if isinstance(bundles, Bundle):
            bundles = [bundles]

        self.bundles = bundles

        if templates is not None:
            self.inject_into_templates(templates)

        if app is not None:
            self.mount(app)

    def inject_into_templates(self, templates):
        template_script = '<script src="/{name}/components.js" type="module"></script>'
        templates.env.globals["svelte_script"] = {
            bundle: template_script.format(name=bundle.name)
            for bundle in self.bundles
        }
        templates.env.globals["svelte_scripts"] = "\n".join(
            templates.env.globals["svelte_script"].values()
        )

    def mount(self, app):
        for bundle in self.bundles:
            dist = pathlib.Path(bundle.components_js_path()).parent
            app.mount(f"/{bundle.name}", StaticFiles(directory=dist), name=bundle.name)
