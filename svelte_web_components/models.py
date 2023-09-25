import json
import os
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from rich import print  # noqa


class NodeEnum(str, Enum):
    download_if_not_present = 'download_if_not_present'
    download = 'download'
    use_system = 'use_system'


class CompilerEnum(str, Enum):
    local_persistent = 'local_persistent'
    local_temporary = 'local_temporary'
    remote = 'remote'


class OutputModeEnum(str, Enum):
    temp_file = 'temp_file'
    memory = 'memory'
    local_path = 'local_path'


class Config(BaseModel):
    name: str
    components: str | os.PathLike
    extra_packages: Optional[str] | Optional[list[str]] | Optional[dict[str, str]] | None = None
    watch: Optional[bool] = False
    environment: Optional[str] = None
    compiler: Optional[CompilerEnum] = CompilerEnum.local_persistent
    compiler_url: Optional[str] = None
    node: Optional[NodeEnum] = NodeEnum.download_if_not_present
    output_mode: Optional[OutputModeEnum] = OutputModeEnum.temp_file
    output: Optional[str] = None
    source_map: Optional[bool] = False

    @staticmethod
    def parse_extra_package(extra_packages: str) -> tuple:
        if isinstance(extra_packages, str):
            extra_packages = extra_packages.split(":")
            if len(extra_packages) == 1:
                return extra_packages[0], "*"
            else:
                return extra_packages[0], extra_packages[1]

    def validate_config(self):

        if self.output_mode == OutputModeEnum.local_path and not self.output:
            raise ValueError("Output path is required when output mode is local_path")
        elif self.output_mode != OutputModeEnum.local_path and self.output:
            print(
                f"In {self.name}: Output path is not required when output mode is {self.output_mode}, it will be ignored")
            self.output = None

        if self.components == "" or self.components is None or not os.path.exists(self.components):
            raise FileNotFoundError(f"Components path {self.components} not found")

        if self.compiler == CompilerEnum.remote and not self.compiler_url:
            raise ValueError("Compiler url is required when compiler is remote")
        elif self.compiler != CompilerEnum.remote and self.compiler_url:
            print(f"In {self.name}: Compiler url is not required when compiler is {self.compiler}, it will be ignored")
            self.compiler_url = None

        if self.output:
            # make it absolute
            self.output = os.path.abspath(self.output)
        if self.components:
            # make it absolute
            self.components = os.path.abspath(self.components)

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
        self.validate_config()

    @classmethod
    def load(cls, config: str | os.PathLike | list[dict] | dict | str | None = None,
             environment: str | None = None) -> "Config":
        if isinstance(config, cls):
            return config
        elif isinstance(config, str) or isinstance(config, os.PathLike):
            return cls.load_from_file(config, environment)
        elif isinstance(config, list) or isinstance(config, dict):
            return cls.load_from_dict(config, environment)
        else:
            raise ValueError("What did you pass to me?")

    @classmethod
    def load_from_dict(cls, data: list[dict] | dict, environment: str | None = None) -> "Config":
        if data is None or data == "" or data == {}:
            raise ValueError("Empty config")
        elif isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            raise ValueError("Invalid config, must be a dict or a list of dicts")

        all_configs = [cls.model_validate(item) for item in data]
        environments = [config.environment for config in all_configs]

        if len(all_configs) == 0:
            raise ValueError("No configs found in file")

        configs = [config for config in all_configs if config.environment == environment]
        if len(configs) == 0:
            raise ValueError(f"No configs found for environment {environment}, available environments: {environments}")
        elif len(configs) == 1:
            return configs[0]
        else:
            raise ValueError(f"Multiple configs for environment {environment} found, specify a unique environment")

    @classmethod
    def load_from_file(cls, file_path: str | os.PathLike, environment: str | None = None) -> "Config":
        """
        Load a config file, perform validation and return a Config object
        :param file_path: Path to the config file
        :param environment: Environment to load, could be None
        :return: Config object: Selected config
        """
        data = None
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")
        with open(file_path) as config_file:
            try:
                data = json.load(config_file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid config file, must be a valid json: {e}")
        return cls.load(data, environment)


class Testa:
    def __init__(self, hello: str):
        self.hello = hello


if __name__ == '__main__':
    print(Config.load_from_file("swc.json", "development"))
