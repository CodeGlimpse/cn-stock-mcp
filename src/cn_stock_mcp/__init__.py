from importlib.metadata import PackageNotFoundError, version

__all__ = ["__version__"]

try:
    __version__ = version("cn-stock-mcp")
except PackageNotFoundError:
    # Source checkouts without an installed distribution remain importable;
    # release and wheel builds always resolve this from package metadata.
    __version__ = "0+unknown"
