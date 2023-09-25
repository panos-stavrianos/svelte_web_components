import asyncio
import os
import signal
import threading
from typing import Optional

import watchfiles

from svelte_web_components import Workspace
from svelte_web_components.models import Config, CompilerEnum, OutputModeEnum
from svelte_web_components.tools import is_async


class Bundle:
    def __init__(self, config: str | os.PathLike | list[dict] | dict | Config | None = None,
                 environment: Optional[str] = None):
        self.environment = environment
        self.config = Config.load(config, environment=environment)
        self.workspace = Workspace()
        self.watch_thread: threading.Thread | None = None
        self.watch_stop_event: threading.Event | None = None
        self.workspace = Workspace()
        self.full_build()

        self.init_watch()

    def init_watch(self):
        if self.config.watch:
            if is_async():
                asyncio.create_task(self.watch_async())
            else:
                self.watch_stop_event = threading.Event()
                signal.signal(signal.SIGINT, self.stop_watch)
                signal.signal(signal.SIGTERM, self.stop_watch)

                self.watch_thread = threading.Thread(target=self.watch_threaded)
                self.watch_thread.start()

    def full_build(self):
        if self.config.compiler == CompilerEnum.remote:
            self.workspace.remote_build(self.config.model_dump())
        else:
            self.workspace.setup_workspace()
            self.workspace.add_project(self.config.name)
            self.workspace.set_components(self.config.name, self.config.components)
            self.workspace.build(self.config.name, self.config.extra_packages, output_path=self.config.output)
            if self.config.compiler == CompilerEnum.local_temporary:
                self.workspace.clean()

    def components_js_path(self):
        if self.config.output_mode == OutputModeEnum.local_path:
            return self.config.output
        return self.workspace.components_js_path(self.config.name)

    def components_js(self):
        return self.workspace.components_js(self.config.name)

    async def watch_async(self):
        async for _ in watchfiles.awatch(self.config.components):
            self.full_build()

    def watch_threaded(self):
        for _ in watchfiles.watch(self.config.components, stop_event=self.watch_stop_event):
            self.full_build()

    def stop_watch(self, *args):
        if self.config.watch and not is_async():
            self.watch_stop_event.set()


if __name__ == '__main__':
    b = Bundle(
        Config(name="testmy",
               components="/home/panos/Downloads/comp",
               output_mode=OutputModeEnum.local_path,
               output="/home/panos/Downloads/comp_dist",
               ))
    print(b.components_js_path())
