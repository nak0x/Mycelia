import importlib
from typing import Any


def import_symbol(path: str) -> Any:
    """
    Import a class or symbol from a dotted path.
    Example: "app.controllers.sample.SampleController"
    """
    if "." not in path:
        raise ValueError(f"Invalid import path: {path}")

    module_path, symbol_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, symbol_name)