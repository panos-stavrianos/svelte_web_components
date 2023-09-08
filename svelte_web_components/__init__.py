__author__ = """Panos Stavrianos"""
__email__ = 'panos@orbitsystems.gr'

from .bundle import Bundle

try:
    from .sveltefiles import SvelteFiles
except ImportError:
    pass
