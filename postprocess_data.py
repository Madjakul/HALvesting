# postprocess_data.py

import logging

from halvesting.utils.data import Postprocessing
from halvesting.utils import PostprocessArgParse, logging_config


logging_config()
WIDTH = 139


if __name__=="__main__":
    args = PostprocessArgParse.parse_known_args()
    logging.info(f"{('=' * WIDTH)}")
    logging.info(f"Generating Data".center(WIDTH))
    logging.info(f"{('=' * WIDTH)}")
    logging.warning(f"Using data from {args.js_folder} and {args.txt_folder}...")
    postprocessing = Postprocessing(
        js_folder=args.js_folder,
        txt_folder=args.txt_folder,
        hf_folder=args.hf_folder
    )
    postprocessing()

