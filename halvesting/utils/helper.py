# halvesting/utils/helper.py

import gzip
import hashlib
import logging
import os

import kenlm
import sentencepiece
from huggingface_hub import hf_hub_download
from tqdm import tqdm

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


def download_sentencepiece_kenlm_models(output_dir_path: str, langs: List[str]):
    """Download Sentencepiece and KenLM language models for supported
    languages.

    Parameters
    ----------
    output_dir_path : str
        Path to the directory where models will be saved.
    langs : List[str]
        Comma-separated list of languages to download models for. Use 'all' for all
        supported languages.
    """
    output_dir_path = check_dir(output_dir_path)

    for lang in tqdm(langs):
        try:
            hf_hub_download(
                repo_id="uonlp/kenlm",
                filename=f"wikipedia_20230501/{lang}.sp.model",
                local_dir=output_dir_path,
                local_dir_use_symlinks=False,
            )
        except:
            logging.warning(
                f"Download failed for Sentencepiece model for language {lang}."
            )

    for lang in tqdm(langs):
        try:
            hf_hub_download(
                repo_id="uonlp/kenlm",
                filename=f"wikipedia_20230501/{lang}.arpa.bin",
                local_dir=output_dir_path,
                local_dir_use_symlinks=False,
            )
        except:
            logging.warning(f"Download failed for KenLM model for language {lang}.")


def load_sentencepiece_model(path_sentencepiece_model: str):
    """Load Sentencepiece model.

    Parameters
    ----------
    path_sentencepiece_model : str
        Path to the Sentencepiece model file.

    Returns
    -------
    sentencepiece_model : sentencepiece.SentencePieceProcessor
        Loaded Sentencepiece model object, or None if loading failed.
    """
    try:
        sentencepiece_model = sentencepiece.SentencePieceProcessor()
        sentencepiece_model.load(path_sentencepiece_model)  # type: ignore
        return sentencepiece_model
    except:
        logging.warning(
            f"Loading Sentencepiece model from {path_sentencepiece_model} failed."
        )
        return None


def load_kenlm_model(path_kenlm_model: str):
    """Load KenLM model.

    Parameters
    ----------
    path_kenlm_model : str
        Path to the KenLM model file.

    Returns
    -------
    kenlm_model : kenlm.Model
        Loaded KenLM model object, or None if loading failed.
    """
    try:
        kenlm_model = kenlm.Model(path_kenlm_model)
        return kenlm_model
    except:
        logging.warning(f"Loading KenLM model from {path_kenlm_model} failed.")
        return None


def tokenize_(text: str, sentencepiece_model: sentencepiece.SentencePieceProcessor):
    """Tokenize text using Sentencepiece model.

    Parameters
    ----------
    text : str
        Input text to tokenize.
    sentencepiece_model : sentencepiece.SentencePieceProcessor
        Loaded Sentencepiece model object.

    Returns
    -------
    tokenized_text : str
        Tokenized text.
    """
    tokenized_text = sentencepiece_model.encode_as_pieces(text)  # type: ignore
    tokenized_text = " ".join(tokenized_text)
    return tokenized_text
