import os
import typing
from datetime import datetime
from email.utils import formatdate
from urllib.parse import quote

from svelte_web_components.bundle import Bundle

try:
    from fastapi import FastAPI
    from starlette._compat import md5_hexdigest
    from starlette.datastructures import Headers
    from starlette.responses import Response
    from starlette.types import Receive, Scope, Send
except ImportError:
    print("ImportError: you need to install fastapi and starlette in order to use SvelteFiles")

PathLike = typing.Union[str, "os.PathLike[str]"]


class NotModifiedResponse(Response):
    NOT_MODIFIED_HEADERS = (
        "cache-control",
        "content-location",
        "date",
        "etag",
        "expires",
        "vary",
    )

    def __init__(self, headers: Headers):
        super().__init__(
            status_code=304,
            headers={
                name: value
                for name, value in headers.items()
                if name in self.NOT_MODIFIED_HEADERS
            },
        )


def is_not_modified(
        response_headers: Headers, request_headers: Headers
) -> bool:
    """
    Given the request and response headers, return `True` if an HTTP
    "Not Modified" response could be returned instead.
    """
    try:
        if_none_match = request_headers["if-none-match"]
        etag = response_headers["etag"]
        if if_none_match == etag:
            print("if_none_match == etag")
            return True
    except KeyError:
        pass

    return False


class SvelteFiles:
    def __init__(self, components: dict[str, str | os.PathLike], extra_packages: list | None = None,
                 app: FastAPI = None,
                 templates=None):
        self.bundler = Bundle(components)
        self.extra_packages = extra_packages
        self.last_modified = datetime.now()

        if templates is not None:
            self.inject_into_templates(templates)

        if app is not None:
            self.mount(app)

    def inject_into_templates(self, templates):
        template_script = '<script src="{component_name}/" type="module"></script>'

        templates.env.globals["svelte_script"] = {
            component_name: template_script.format(component_name=component_name)
            for component_name in self.bundler.components.keys()
        }
        templates.env.globals["svelte_scripts"] = "\n".join(
            template_script.format(component_name=component_name)
            for component_name in self.bundler.components.keys()
        )

    def mount(self, app):
        for component_name in self.bundler.components.keys():
            app.mount(component_name, self)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        The ASGI entry point.
        """
        assert scope["type"] == "http"
        component_name = scope["raw_path"].decode("utf-8").rstrip("/")

        response = Response(self.bundler[component_name], media_type="application/javascript")

        stat = self.get_stat(component_name)
        content_disposition = f'inline; filename="{quote(component_name) + ".js"}"'

        response.headers.setdefault("content-disposition", content_disposition)

        response.headers.setdefault("content-length", stat["content_length"])
        response.headers.setdefault("last-modified", stat["last_modified"])
        response.headers.setdefault("etag", stat["etag"])

        if is_not_modified(response.headers, request_headers=Headers(scope=scope)):
            print("NotModifiedResponse")
            response = NotModifiedResponse(response.headers)

        await response(scope, receive, send)

    def get_stat(self, component_name: str) -> dict[str, str]:
        content_length = str(len(self.bundler[component_name]))
        last_modified = formatdate(self.last_modified.timestamp(), usegmt=True)
        etag_base = f"{last_modified}{content_length}"
        etag = md5_hexdigest(etag_base.encode(), usedforsecurity=False)
        return {"content_length": content_length, "last_modified": last_modified, "etag": etag}
