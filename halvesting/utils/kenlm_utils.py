# halvesting/utils/kenlm_utils.py

import logging
from typing import List

import kenlm
import sentencepiece
from huggingface_hub import hf_hub_download
from tqdm import tqdm

from halvesting.utils.utils import check_dir


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
