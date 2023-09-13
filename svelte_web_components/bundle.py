import asyncio
import configparser
import os
import signal
import threading

from watchfiles import awatch, watch

from svelte_web_components import Workspace


def is_async():
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


class Bundle:
    def __init__(self, name: str,
                 components: str | os.PathLike = "",
                 extra_packages: str | list[str] | dict[str, str] | None = None,
                 config_file="swc.config",
                 watch: bool = False):
        if config_file and os.path.exists(config_file):

            config = configparser.ConfigParser()
            if not config.read(config_file):
                raise ValueError(f"Config file {config_file} not found")
            config.read(config_file)
            if name in config:
                components = config[name].get('components', components)

                extra_packages = config[name].get('extra_packages', extra_packages)  # todo: fix this
                watch = config[name].getboolean('watch', watch)

        self.name = name
        self.components_path = components
        self.extra_packages = extra_packages

        self.watch = watch
        if not self.components_path:
            raise ValueError("Components path not specified")
        if not os.path.exists(self.components_path):
            raise ValueError(f"Components path {self.components_path} does not exist")
        if not os.path.isdir(self.components_path):
            raise ValueError(f"Components path {self.components_path} is not a directory")

        self.workspace = Workspace()
        self.full_build()
        if self.watch:
            if is_async():
                asyncio.create_task(self.watch_async())
            else:
                self.watch_stop_event = threading.Event()
                signal.signal(signal.SIGINT, self.stop_watch)
                signal.signal(signal.SIGTERM, self.stop_watch)

                self.watch_thread = threading.Thread(target=self.watch_threaded)
                self.watch_thread.start()

    def full_build(self):
        self.workspace.setup_workspace()
        self.workspace.add_project(self.name)
        self.workspace.set_components(self.name, self.components_path)
        self.workspace.build(self.name, self.extra_packages)

    def components_js_path(self):
        return self.workspace.components_js_path(self.name)

    def components_js(self):
        return self.workspace.components_js(self.name)

    async def watch_async(self):
        async for _ in awatch(self.components_path):
            self.full_build()

    def watch_threaded(self):
        for _ in watch(self.components_path, stop_event=self.watch_stop_event):
            self.full_build()

    def stop_watch(self, *args):
        if self.watch and not is_async():
            self.watch_stop_event.set()


if __name__ == '__main__':
    b = Bundle("test",
               components="/mnt/Inner Space/Projects/PycharmProjects/KeyCloud/app/templates/components",
               extra_packages="svelte-multiselect")
