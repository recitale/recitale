from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("recitale")
except PackageNotFoundError:
    pass
