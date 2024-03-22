# halvesting/utils/service_utils.py

import logging
import os


def check_dir(path: str):
    """Check if there is a directory at ``path`` and creates it if necessary.

    Parameters
    ----------
    path: str
        Path to the directory.

    Returns
    -------
    path: str
        Path to the existing directory.
    """
    if os.path.isdir(path):
        return path
    logging.warning(f"No folder with name {path}: creating folder at path.")
    os.makedirs(path)
    return path
