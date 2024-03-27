# enrish.py

import json
import logging
import os

import datasets
from fasttext.FastText import _FastText
from nltk.tokenize import WordPunctTokenizer
from transformers import AutoTokenizer

from halvesting.utils import (EnrisherArgParse,
                              download_sentencepiece_kenlm_models,
                              load_kenlm_model, load_sentencepiece_model,
                              logging_config)

WIDTH = 139
logging_config()


if __name__ == "__main__":
    args = EnrisherArgParse.parse_known_args()
    logging.info(f"{('=' * WIDTH)}")
    logging.info(f"Enrishing data from HF dataset".center(WIDTH))
    logging.info(f"{('=' * WIDTH)}")

    with open(args.lang_to_iso, "r", encoding="utf-8") as jsf:
        lang_to_iso = json.load(jsf)
    iso_to_lang = {v: k for k, v in lang_to_iso.items()}
    with open(args.config_path, "r", encoding="utf-8") as f:
        configs = list(set(f.read().splitlines()))
    langs_id = [
        {
            "lang": iso_to_lang[config],
            "dataset_id": config,
            "stopwords_id": config,
            "flagged_words_id": config,
            "fasttext_id": config,
            "sentencepiece_id": config,
            "kenlm_id": config,
        }
        for config in configs
    ]

    if args.download_models:  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        download_sentencepiece_kenlm_models(
            output_dir_path=args.output_dir_path, langs=args.langs
        )

    # if args.dataset_config_names is None:
    #     configs = datasets.get_dataset_config_names(args.dataset_name)

    # else:
    #     configs = args.dataset_config_names.split(",")

    # datasets_list = [
    #     datasets.load_dataset(args.dataset_name, config, split="train")
    #     for config in configs
    # ]

    # default_langs = ["en", "fr"]
    # langid_model = _FastText(args.fasttext_model_file)
    # tokenizer = AutoTokenizer.from_pretrained(args.hf_model_name)
    # word_tokenizer = WordPunctTokenizer()
    # for dataset, lang in zip(datasets_list, configs):
    #     print(f"Processing {lang}...")
    #     print(f"Loading sentencepiece and kenlm models for {lang}...")
    #     all_sentencepiece_models = {
    #         lang: load_sentencepiece_model(
    #             os.path.join(args.kenlm_dir_path, f"{lang}.sp.model")
    #         )
    #         for lang in list(set(default_langs + [lang]))
    #     }
    #     all_kenlm_models = {
    #         lang: load_kenlm_model(
    #             os.path.join(args.kenlm_dir_path, f"{lang}.arpa.bin")
    #         )
    #         for lang in list(set(default_langs + [lang]))
    #     }
    #     print(f"DONE: Loading sentencepiece and kenlm models for {lang}...")
    #     dataset: datasets.Dataset = dataset.map(
    #         lambda x: enrish(
    #             x,
    #             all_sentencepiece_models,
    #             all_kenlm_models,
    #             tokenizer,
    #             word_tokenizer,
    #             langid_model,
    #         ),
    #         batched=True,
    #         batch_size=1000,
    #         num_proc=args.num_proc,
    #     )
    #     print(f"Saving processed dataset for {lang}...")
    #     # dataset.save_to_disk(os.path.join(args.output_dir_path, lang))
    #     # dump as jsonl
    #     with open(os.path.join(args.output_dir_path, lang, f"{lang}.jsonl"), "w") as f:
    #         for item in dataset:
    #             f.write(json.dumps(item, ensure_ascii=True) + "\n")
