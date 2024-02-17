# fetch_data.py

import logging

from halversting.api import HAL
from halversting.utils import  FetcherArgParse, logging_config


logging_config()
WIDTH = 139


if __name__=="__main__":
    args = FetcherArgParse.parse_known_args()
    logging.info(f"{('=' * WIDTH)}")
    logging.info(f"Fetching from HAL".center(WIDTH))
    logging.info(f"{('=' * WIDTH)}")
    logging.warning(f"Requesting {args.query} from HAL...")
    hal = HAL(
        query=args.query if args.query else None,
        from_date=args.from_date if args.from_date else None,
        from_hour=args.from_hour if args.from_hour else None,
        to_date=args.to_date if args.to_date else None,
        to_hour=args.to_hour if args.to_hour else None,
        pdf=args.pdf
    )
    hal()

