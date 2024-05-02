# run_experiments.py

import json
import logging
import os

import datasets
from tqdm import tqdm

from halvesting.experiments import (count_doc_and_tokens,
                                    count_raw_doc_and_tokens)
from halvesting.utils import (WIDTH, ExperimentsArgParse, check_dir,
                              logging_config)

logging_config()


if __name__ == "__main__":
    args = ExperimentsArgParse.parse_known_args()
    logging.info(f"{('=' * WIDTH)}")
    logging.info(f"Enrishing data from HF dataset".center(WIDTH))
    logging.info(f"{('=' * WIDTH)}")

    with open(args.dataset_config_path, "r", encoding="utf-8") as f:
        configs = f.read().splitlines()

    for lang in tqdm(configs):
        logging.info(f"Loading {lang} dataset...")
        dataset = datasets.load_dataset(
            args.dataset_checkpoint,
            lang,
            split="train",
            cache_dir=(
                check_dir(args.cache_dir_path)
                if args.cache_dir_path is not None
                else "~/.cache/huggingface/datasets"
            ),
        )
        if args.count_raw_tokens:
            logging.info("Counting raw documents and tokens...")
            stats = count_raw_doc_and_tokens(dataset)  # type: ignore
        logging.info("Counting documents and tokens...")
        stats = count_doc_and_tokens(dataset, args.batch_size, args.num_proc)  # type: ignore
        output_file_path = os.path.join(check_dir(args.output_dir_path), f"{lang}.json")
        with open(output_file_path, "w") as f:
            json.dump(stats, f, indent=4)
