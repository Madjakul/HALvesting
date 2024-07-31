# fetch_data.py

import logging

from halvesting.services import HAL, PDF
from halvesting.utils import WIDTH, FetcherArgParse, logging_config

logging_config()


if __name__ == "__main__":
    args = FetcherArgParse.parse_known_args()
    logging.info(f"{('=' * WIDTH)}")
    logging.info(f"Fetching Data from HAL".center(WIDTH))
    logging.info(f"{('=' * WIDTH)}")
    logging.info(f"Requesting {args.query} from HAL...")
    hal = HAL(
        query=args.query if args.query else None,
        from_date=args.from_date if args.from_date else None,
        from_hour=args.from_hour if args.from_hour else None,
        to_date=args.to_date if args.to_date else None,
        to_hour=args.to_hour if args.to_hour else None,
        response_dir=args.response_dir,
    )
    hal()

    if args.pdf:
        logging.info(f"{('=' * WIDTH)}")
        logging.info(f"Downloading PDFs from HAL".center(WIDTH))
        logging.info(f"{('=' * WIDTH)}")
        PDF.download(
            response_dir=args.response_dir,
            pdf_dir=args.pdf_dir,
            num_chunks=args.num_chunks,
        )
