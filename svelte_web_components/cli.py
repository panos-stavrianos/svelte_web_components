import click

from svelte_web_components.setup_node import setup_node


@click.command()
@click.option('--clean', is_flag=True, help='Remove current setup and re-install')
def init(clean):
    setup_node(clean)


if __name__ == '__main__':
    init()
