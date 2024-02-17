# utils/arg_parse.py

import argparse


class FetcherArgParse():
    """Argument parser used to fetch data from HAL.
    """

    @classmethod
    def parse_known_args(cls):
        """Parses arguments to correctly fetch data from online repositories.

        Returns
        -------
        args: Any
            Parsed arguments.
        """
        parser = argparse.ArgumentParser(
            description="Arguments used to fetch data."
        )
        parser.add_argument(
            "--query",
            type=str,
            nargs="?",
            const=None,
            help="Query used to request APIs."
        )
        parser.add_argument(
            "--from_date",
            type=str,
            default=argparse.SUPPRESS,
            help="Date of the last update"
        )
        parser.add_argument(
            "--from_hour",
            type=str,
            default=argparse.SUPPRESS,
            help="Hour of the last update"
        )
        parser.add_argument(
            "--to_date",
            type=str,
            default=argparse.SUPPRESS,
            help="Date of the last document submitted."
        )
        parser.add_argument(
            "--to_hour",
            type=str,
            default=argparse.SUPPRESS,
            help="Hour of the last document submitted."
        )
        parser.add_argument(
            "--pdf",
            action="store_true",
            help="If you want PDFs to be downloaded on the fly or not."
        )
        args, _ = parser.parse_known_args()
        return args


class PostprocessArgParse():
    """Argument parser used to build data for HuggingFace.
    """

    @classmethod
    def parse_known_args(cls):
        """Parses arguments.

        Returns
        -------
        args: Any
            Parsed arguments.
        """
        parser = argparse.ArgumentParser(
            description="Arguments used to fetch data."
        )
        parser.add_argument(
            "--js_folder",
            type=str,
            required=True,
            help="Folder containing fetched data."
        )
        parser.add_argument(
            "--txt_folder",
            type=str,
            required=True,
            help="Folder containing the txt files."
        )
        parser.add_argument(
            "--hf_folder",
            type=str,
            required=True,
            help="Final folder containing the processed data for HuggingFace."
        )
        args, _ = parser.parse_known_args()
        return args

