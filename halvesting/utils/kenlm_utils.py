# halvesting/utils/kenlm_utils.py

import logging
import os

import kenlm
import sentencepiece
from huggingface_hub import hf_hub_download
from tqdm import tqdm

from halvesting.utils import check_dir

HF_TOKEN = os.getenv("HF_TOKEN")


def download_sentencepiece_kenlm_models(output_dir_path: str, langs: str):
    """Download Sentencepiece and KenLM language models for supported
    languages.

    Parameters
    ----------
    output_dir_path: str
        Path to the directory where models will be saved.
    langs: str
        Comma-separated list of languages to download models for. Use 'all' for all
        supported languages.
    """
    output_dir_path = check_dir(output_dir_path)
    supported_sentencepiece_langs = LANGS_ID["sentencepiece_id"].dropna().unique()
    supported_kenlm_langs = LANGS_ID["kenlm_id"].dropna().unique()

    if langs == "all":
        selected_sentencepiece_langs = supported_sentencepiece_langs
        selected_kenlm_langs = supported_kenlm_langs
    else:
        langs_ = langs.split(",")
        # check if all languages are supported
        assert all(
            lang in supported_sentencepiece_langs for lang in langs_
        ), """Please specify a valid language or use 'all' to download all supported \
            languages.
            """
        assert all(
            lang in supported_kenlm_langs for lang in langs_
        ), """Please specify a valid language or use 'all' to download all supported \
            languages.
            """
        selected_kenlm_langs = langs_
        selected_sentencepiece_langs = langs_

    for lang in tqdm(selected_sentencepiece_langs):
        try:
            hf_hub_download(
                repo_id="uonlp/kenlm",
                filename=f"wikipedia_20230501/{lang}.sp.model",
                local_dir=output_dir_path,
                local_dir_use_symlinks=False,
            )
        except:
            logging.warning(
                f"Warning: Download failed for Sentencepiece model for language {lang}."
            )

    for lang in tqdm(selected_kenlm_langs):
        try:
            hf_hub_download(
                repo_id="uonlp/kenlm",
                filename=f"wikipedia_20230501/{lang}.arpa.bin",
                local_dir=output_dir_path,
                local_dir_use_symlinks=False,
            )
        except:
            logging.warning(
                f"Warning: Download failed for KenLM model for language {lang}."
            )


def load_sentencepiece_model(path_sentencepiece_model: str):
    try:
        sentencepiece_model = sentencepiece.SentencePieceProcessor()
        sentencepiece_model.load(path_sentencepiece_model)
        return sentencepiece_model
    except:
        logging.error(
            f"Loading Sentencepiece model from {path_sentencepiece_model} failed."
        )
        return None


def load_kenlm_model(path_kenlm_model: str):
    try:
        kenlm_model = kenlm.Model(path_kenlm_model)
        return kenlm_model
    except:
        logging.error(f"Loading KenLM model from {path_kenlm_model} failed.")
        return None
