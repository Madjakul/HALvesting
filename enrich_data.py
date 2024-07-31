# enrich_data.py

import json
import logging
import os

import datasets
from transformers import AutoTokenizer

from halvesting.services import enrich
from halvesting.utils import (WIDTH, EnricherArgParse, compress,
                              download_sentencepiece_kenlm_models,
                              load_kenlm_model, load_sentencepiece_model,
                              logging_config)

_NUM_DOC_PER_FILE = 10000
logging_config()


if __name__ == "__main__":
    args = EnricherArgParse.parse_known_args()
    logging.info(f"{('=' * WIDTH)}")
    logging.info(f"Enriching data from HF dataset".center(WIDTH))
    logging.info(f"{('=' * WIDTH)}")

    with open(args.dataset_config_path, "r", encoding="utf-8") as f:
        configs = f.read().splitlines()

    if args.download_models:
        download_sentencepiece_kenlm_models(
            output_dir_path=args.kenlm_dir_path, langs=configs
        )

    for lang in configs:
        logging.info(f"Loading {lang} dataset...")
        dataset = datasets.load_dataset(
            args.dataset_checkpoint,
            lang,
            split="train",
            cache_dir=(
                args.cache_dir_path
                if args.cache_dir_path is not None
                else "~/.cache/huggingface/datasets"
            ),
        )
        logging.info(f"Loading sentencepiece and kenlm models for {lang}...")
        sentencepiece_model = load_sentencepiece_model(
            os.path.join(args.kenlm_dir_path, f"wikipedia_20230501/{lang}.sp.model")
        )
        kenlm_model = load_kenlm_model(
            os.path.join(args.kenlm_dir_path, f"wikipedia_20230501/{lang}.arpa.bin")
        )
        logging.info(f"DONE: Loading sentencepiece and kenlm models for {lang}...")
        dataset = dataset.map(
            lambda x: enrich(
                x,
                sentencepiece_model=sentencepiece_model,
                kenlm_model=kenlm_model,
                lang=lang,
                tokenizer=(
                    AutoTokenizer.from_pretrained(
                        args.tokenizer_checkpoint, use_fast=args.use_fast
                    )
                    if args.tokenizer_checkpoint
                    else None
                ),
            ),
            batched=True,
            batch_size=args.batch_size,
            num_proc=args.num_proc,  # type: ignore
            load_from_cache_file=args.load_from_cache_file,  # type: ignore
        )
        logging.info(f"Saving processed dataset for {lang}...")
        os.makedirs(os.path.join(args.output_dir_path, lang), exist_ok=True)
        counter = 0
        idx = 0
        output_path = os.path.join(
            args.output_dir_path, lang, f"{lang}{args.version}-{counter}.jsonl"
        )
        for item in dataset:
            with open(output_path, "a") as jsf:
                jsf.write(json.dumps(item, ensure_ascii=False) + "\n")
            idx += 1
            if idx % _NUM_DOC_PER_FILE == 0:
                logging.info(f"Compressing {output_path}...")
                compress(
                    lang=lang,
                    hf_dir_path=args.output_dir_path,
                    counter=counter,
                    version=args.version,
                )
                counter += 1
                output_path = os.path.join(
                    args.output_dir_path, lang, f"{lang}{args.version}-{counter}.jsonl"
                )
        logging.info(f"Compressing {output_path}...")
        compress(
            lang=lang,
            hf_dir_path=args.output_dir_path,
            counter=counter,
            version=args.version,
        )
