import os
import sys
import importlib.metadata


def is_windows():
    """
    :return: Returns true if the local system/OS name is Windows.
    """
    return os.name == "nt"


def get_entry_points(namespace):
    if sys.version_info >= (3, 10):
        return importlib.metadata.entry_points(group=namespace)
    else:
        try:
            return importlib.metadata.entry_points().get(namespace, [])
        except AttributeError:
            return importlib.metadata.entry_points().select(group=namespace)
