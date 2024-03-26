# %%
import argparse
import json
import os

import datasets
import ftfy
import kenlm
import pandas as pd
import sentencepiece
from fasttext.FastText import _FastText
from nltk.tokenize import WordPunctTokenizer
from transformers import AutoTokenizer

from ..utils.data.postprocessing import Postprocessing
from ..utils.service_utils import (
    digits_re,
    non_printing_characters_re,
    unicode_punctuation,
)


def remove_non_printing_characters(document, non_printing_characters_re):
    return non_printing_characters_re.sub("", document)


def uniform_whitespace(
    document,
    whitespace=[
        " ",
        " ",
        " ",
        " ",
        " ",
        "　",
        " ",
        " ",
        " ",
        " ",
        "￼",
        "",
    ],
):
    """There are different whitespace characters."""
    whitespace = set(whitespace)
    document = "".join([char if char not in whitespace else " " for char in document])
    return document


def replace_digits_with_zeros(document=None, digits_re=None):
    return digits_re.sub("0", document)


def replace_unicode_punctuation(document, unicode_punctuation):
    return "".join(unicode_punctuation.get(c, c) for c in document)


def normalization(
    document,
    do_remove_non_printing_characters,
    strip,
    lower_case,
    do_uniform_whitespace,
    do_replace_digits_with_zeros,
    do_replace_unicode_punctuation,
    non_printing_characters_re=non_printing_characters_re,
    digits_re=digits_re,
    unicode_punctuation=unicode_punctuation,
):
    if do_remove_non_printing_characters:
        document = remove_non_printing_characters(document, non_printing_characters_re)
    if strip:
        document = document.strip()
    if not document:
        return document
    if lower_case:
        document = document.lower()
    if do_uniform_whitespace:
        document = uniform_whitespace(document)
    if do_replace_digits_with_zeros:
        document = replace_digits_with_zeros(document, digits_re)
    if do_replace_unicode_punctuation:
        document = replace_unicode_punctuation(document, unicode_punctuation)
    return document


def tokenization(document, sentencepiece_model, join_on_whitespace):
    document_tokenized = sentencepiece_model.encode_as_pieces(document)
    if join_on_whitespace:
        document_tokenized = " ".join(document_tokenized)
    return document_tokenized


fasttext_model_file = os.getenv("FASTTEXT_MODEL_FILE")


def detect_lang(text, langid_model):
    language, score = langid_model.predict(text.replace("\n", ""))
    language = language[0].split("__")[2]
    return {"lang": language, "score": score[0]}


def compute_perplexity_score(
    document, sentencepiece_models, kenlm_models, langid_model
):
    document = normalization(
        document=document,
        do_remove_non_printing_characters=True,
        strip=True,
        lower_case=False,
        do_uniform_whitespace=True,
        do_replace_digits_with_zeros=True,
        do_replace_unicode_punctuation=True,
    )

    doc_log_score, doc_length = 0, 0
    for line in document.split("\n"):
        lang = detect_lang(line, langid_model)["lang"]
        if lang not in sentencepiece_models:
            # doc_length += len(line.split()) + 1
            doc_length += 0.00000000001
            doc_log_score += 0.00000000001
            continue
        line = tokenization(line, sentencepiece_models[lang], join_on_whitespace=True)
        log_score = kenlm_models[lang].score(line)
        length = len(line.split()) + 1
        doc_log_score += log_score
        doc_length += length
    pp_score = 10.0 ** (-doc_log_score / doc_length)
    pp_score = round(pp_score, 1)
    return pp_score


def load_sentencepiece_model(path_sentencepiece_model):
    try:
        sentencepiece_model = sentencepiece.SentencePieceProcessor()
        sentencepiece_model.load(path_sentencepiece_model)
        return sentencepiece_model
    except:
        print(
            f"Error: Loading Sentencepiece model from {path_sentencepiece_model} failed."
        )
        return None


def load_kenlm_model(path_kenlm_model):
    try:
        kenlm_model = kenlm.Model(path_kenlm_model)
        return kenlm_model
    except:
        print(f"Error: Loading KenLM model from {path_kenlm_model} failed.")
        return None


def enrish(
    document,
    sentencepiece_models,
    kenlm_models,
    tokenizer,
    word_tokenizer,
    langid_model,
):
    document["text"] = (
        ftfy.fix_text(document["text"]).replace("\u202b", "").replace("\u202c", "")
    )
    document["kenlm_pp"] = compute_perplexity_score(
        document["text"], sentencepiece_models, kenlm_models, langid_model
    )

    _document = Postprocessing(document["text"], tokenizer, word_tokenizer)

    document["rps_doc_word_count"] = _document.rps_doc_word_count()
    document["token_count"] = _document.count_tokens(document["text"])
    document["rps_doc_frac_all_caps_words"] = _document.rps_doc_frac_all_caps_words()
    document["rps_doc_frac_no_alph_words"] = _document.rps_doc_frac_no_alph_words()
    document["rps_doc_lorem_ipsum"] = _document.rps_doc_lorem_ipsum()
    document["rps_doc_mean_word_length"] = _document.rps_doc_mean_word_length()
    document["rps_doc_symbol_to_word_ratio"] = _document.rps_doc_symbol_to_word_ratio()
    document["rps_doc_frac_unique_words"] = _document.rps_doc_frac_unique_words()

    return document


def main(args):

    if args.dataset_config_names is None:
        configs = datasets.get_dataset_config_names(args.dataset_name)

    else:
        configs = args.dataset_config_names.split(",")

    # get kwargs from args
    # expectation: --kwargs key1=value1,key2=value2
    kwargs_str = args.kwargs
    kwargs = dict()
    if kwargs_str is not None:
        kwargs_str = kwargs_str.split(",")
        for kwarg in kwargs_str:
            key, value = kwarg.split("=")
            kwargs[key] = value

    datasets_list = [
        datasets.load_dataset(args.dataset_name, config, split="train", **kwargs)
        for config in configs
    ]

    default_langs = ["en", "fr"]
    langid_model = _FastText(args.fasttext_model_file)
    tokenizer = AutoTokenizer.from_pretrained(args.hf_model_name)
    word_tokenizer = WordPunctTokenizer()
    for dataset, lang in zip(datasets_list, configs):
        print(f"Processing {lang}...")
        print(f"Loading sentencepiece and kenlm models for {lang}...")
        all_sentencepiece_models = {
            lang: load_sentencepiece_model(
                os.path.join(args.kenlm_dir_path, f"{lang}.sp.model")
            )
            for lang in list(set(default_langs + [lang]))
        }
        all_kenlm_models = {
            lang: load_kenlm_model(
                os.path.join(args.kenlm_dir_path, f"{lang}.arpa.bin")
            )
            for lang in list(set(default_langs + [lang]))
        }
        print(f"DONE: Loading sentencepiece and kenlm models for {lang}...")
        dataset: datasets.Dataset = dataset.map(
            lambda x: enrish(
                x,
                all_sentencepiece_models,
                all_kenlm_models,
                tokenizer,
                word_tokenizer,
                langid_model,
            ),
            batched=False,
            num_proc=None,
        )
        print(f"Saving processed dataset for {lang}...")
        # dataset.save_to_disk(os.path.join(args.output_dir_path, lang))
        # dump as jsonl
        with open(os.path.join(args.output_dir_path, lang, f"{lang}.jsonl"), "w") as f:
            for item in dataset:
                f.write(json.dumps(item, ensure_ascii=True) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset_name",
        type=str,
        help="Name of the dataset to be processed.",
    )
    parser.add_argument(
        "--dataset_config_names",
        type=str,
        default=None,
        help="Comma-separated list of dataset config names to be processed.",
    )
    parser.add_argument(
        "--kenlm_dir_path",
        type=str,
        help="Path to the directory containing the sentencepiece and kenlm models.",
    )
    parser.add_argument(
        "--fasttext_model_file",
        type=str,
        help="Path to the fasttext model file.",
    )
    parser.add_argument(
        "--hf_model_name",
        type=str,
        default="google/mt5-small",
        help="Name of the Hugging Face model to be used for tokenization.",
    )
    parser.add_argument(
        "--output_dir_path",
        type=str,
        help="Path to the directory where the processed dataset will be saved.",
    )
    parser.add_argument(
        "--num_proc",
        type=int,
        default=1,
        help="Number of processes to use for processing the dataset.",
    )
    parser.add_argument(
        "--kwargs",
        type=str,
        help="Additional keyword arguments to be passed to the dataset loading function. ex: --kwargs key1=value1,key2=value2",
    )
    args = parser.parse_args()
    main(args)
