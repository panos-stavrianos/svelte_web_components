import click
from rich.console import Console

from svelte_web_components import Workspace

console = Console()


@click.group()
def cli():
    pass


@cli.command("init")
@click.option('--clean', is_flag=True, default=False, help='Remove current setup and re-install')
def init(clean):
    Workspace().setup_workspace(clean)
    console.print("Workspace initialized", style="bold green")


@cli.command("ls")
def ls():
    projects = Workspace().ls()
    if projects:
        console.print("Projects:", style="bold green")
        for project in projects:
            console.print(f"  - {project}")


@cli.command("add")
@click.argument('name', required=True)
def add(name):
    Workspace().add_project(name)
    console.print(f"Project {name} added", style="bold green")


@cli.command("rm")
@click.argument('name', required=True)
def rm(name):
    Workspace().rm_project(name)
    console.print(f"Project {name} removed", style="bold green")


@cli.command("set")
@click.argument('name', required=True)
@click.argument('components_path', required=True)
def set_components(name, components_path):
    Workspace().set_components(name, components_path)
    console.print(f"Components path set to {components_path} for project {name}", style="bold green")


@cli.command("build")
@click.argument('name', required=True)
def build(name):
    Workspace().build(name)
    console.print(f"Project {name} built", style="bold green")


if __name__ == '__main__':
    cli()
