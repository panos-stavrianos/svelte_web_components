import json
import os
from typing import Optional

from pydantic import BaseModel, TypeAdapter
from rich import print  # noqa


class Project(BaseModel):
    name: str
    components: Optional[str | os.PathLike] = None
    extra_packages: Optional[str | list[str] | dict[str, str] | None] = None
    watch: Optional[bool] = False

    def parse_extra_package(self, extra_packages: str) -> tuple:
        if not extra_packages:
            return {}
        if isinstance(extra_packages, str):
            extra_packages = extra_packages.split(":")
            if len(extra_packages) == 1:
                return extra_packages[0], "*"
            else:
                return extra_packages[0], extra_packages[1]

    def model_post_init(self, __context) -> None:
        if not self.extra_packages:
            self.extra_packages = {}
        if isinstance(self.extra_packages, str):
            name, version = self.parse_extra_package(self.extra_packages)
            self.extra_packages = {name: version}

        if isinstance(self.extra_packages, list):
            packages = {}
            for package in self.extra_packages:
                name, version = self.parse_extra_package(package)
                packages[name] = version
            self.extra_packages = packages


def parse_config_json(config: str | list | dict) -> list[Project]:
    if isinstance(config, str):
        config = json.loads(config)
    if isinstance(config, dict):
        config = [config]
    projects_adapter = TypeAdapter(list[Project])
    return projects_adapter.validate_python(config)


def parse_config_file(config_file: str | os.PathLike) -> list[Project]:
    with open(config_file) as swc_file:
        return parse_config_json(json.load(swc_file))


if __name__ == '__main__':
    p1 = Project(name="p1", components="components/c1", extra_packages=["moment", "opt:^3.3"], watch=True)
    p2 = Project(name="p2", components="components/c1", extra_packages="moment", watch=True)

    print(parse_config_file("swc.json"))
