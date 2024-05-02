# halvesting/utils/utils.py

import gzip
import hashlib
import logging
import os

WIDTH = 139
PROJECT_ROOT = os.getcwd()
DATA_ROOT = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_ROOT, exist_ok=True)


def _generate_checksum(base_dir_path: str, gz_file_path: str):
    """Generates a checksum for the compressed tarball file.

    Parameters
    ----------
    lang : str
        ISO 639 language code.
    folder : str
        Path to the folder.
    tgz_filename : str
        Name of the compressed tarball file.
    """
    checksum_file_path = os.path.join(base_dir_path, "checksum.sha256")

    hasher = hashlib.sha256()
    with open(gz_file_path, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            hasher.update(chunk)

    checksum = hasher.hexdigest()
    with open(checksum_file_path, "a") as f:
        f.write(f"{checksum}\t{os.path.basename(gz_file_path)}\n")


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
    logging.warning(f"No folder at {path}: creating folders at path.")
    os.makedirs(path)
    return path


def compress(lang: str, hf_dir_path: str, counter: int, version: str):
    """Compresses the JSON lines files for a given language into a tarball.

    Parameters
    ----------
    lang : str
        ISO 639 language code.
    """
    base_dir_path = check_dir(os.path.join(hf_dir_path, lang))
    base_file_path = os.path.join(base_dir_path, f"{lang}{version}-{counter}")
    jsl_file_path = f"{base_file_path}.jsonl"
    gz_file_path = f"{jsl_file_path}.gz"
    with open(jsl_file_path, "rb") as f:
        with gzip.open(gz_file_path, "wb") as gzf:
            gzf.writelines(f)
    os.remove(jsl_file_path)
    _generate_checksum(base_dir_path=base_dir_path, gz_file_path=gz_file_path)
