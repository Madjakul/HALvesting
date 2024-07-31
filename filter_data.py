# filter_data.py

import json
import logging
import os

import datasets

from halvesting.services import filter_
from halvesting.utils import WIDTH, FilteringArgParse, compress, logging_config

NUM_DOC_PER_FILE = 10000
COLUMNS = [
    "token_count",
    "rps_doc_frac_all_caps_words",
    "rps_doc_frac_lines_end_with_ellipsis",
    "rps_doc_frac_no_alph_words",
    "rps_doc_lorem_ipsum",
    "rps_doc_mean_word_length",
    "rps_doc_stop_word_fraction",
    "rps_doc_symbol_to_word_ratio",
    "rps_doc_frac_unique_words",
    "rps_doc_unigram_entropy",
    "rps_doc_word_count",
    "doc_frac_lines_ending_with_terminal_punctution_mark",
    "rps_lines_frac_start_with_bulletpoint",
    "rps_doc_num_sentences",
    "rps_frac_chars_in_dupe_5grams",
    "rps_frac_chars_in_dupe_6grams",
    "rps_frac_chars_in_dupe_7grams",
    "rps_frac_chars_in_dupe_8grams",
    "rps_frac_chars_in_dupe_9grams",
    "rps_frac_chars_in_dupe_10grams",
    "kenlm_pp",
]
logging_config()


if __name__ == "__main__":
    args = FilteringArgParse.parse_known_args()
    logging.info(f"{('=' * WIDTH)}")
    logging.info(f"Filtering data from HF dataset".center(WIDTH))
    logging.info(f"{('=' * WIDTH)}")

    with open(args.dataset_config_path, "r", encoding="utf-8") as f:
        configs = f.read().splitlines()

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
        pre_len = len(dataset)  # type: ignore
        dataset = dataset.filter(
            lambda batch: filter_(batch),
            batched=True,
            batch_size=args.batch_size,
            num_proc=args.num_proc,  # type: ignore
            load_from_cache_file=args.load_from_cache_file,  # type: ignore
        )
        dataset = dataset.remove_columns(COLUMNS)
        post_len = len(dataset)
        logging.info(f"Filtered {pre_len - post_len} for {lang}.")
        if post_len == 0:
            continue
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
            if idx % NUM_DOC_PER_FILE == 0:
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
