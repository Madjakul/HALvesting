# merge_data.py

import logging

from halvesting.services import Merger
from halvesting.utils import WIDTH, MergerArgParse, logging_config

logging_config()


if __name__ == "__main__":
    args = MergerArgParse.parse_known_args()
    logging.info(f"{('=' * WIDTH)}")
    logging.info(f"Generating Data".center(WIDTH))
    logging.info(f"{('=' * WIDTH)}")
    logging.info(f"Using data from {args.js_dir_path} and {args.txts_dir_path}...")
    merger = Merger(
        js_dir_path=args.js_dir_path,
        txts_dir_path=args.txts_dir_path,
        output_dir_path=args.output_dir_path,
        version=args.version,
    )
    merger()
