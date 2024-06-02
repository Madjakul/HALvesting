# utils/arg_parse.py

import argparse
from typing import Union


def _bool(v: Union[str, int, bool]):
    if isinstance(v, bool):
        return v
    elif isinstance(v, str):
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0"):
            return False
    elif isinstance(v, int):
        if v == 1:
            return True
        else:
            return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


class FetcherArgParse:
    """Argument parser used to fetch data from HAL."""

    @classmethod
    def parse_known_args(cls):
        """Parses arguments to correctly fetch data from online repositories.

        Returns
        -------
        args: Any
            Parsed arguments.
        """
        parser = argparse.ArgumentParser(description="Arguments used to fetch data.")
        parser.add_argument(
            "--query",
            type=str,
            nargs="?",
            const=None,
            help="Query used to request APIs.",
        )
        parser.add_argument(
            "--from_date",
            type=str,
            nargs="?",
            const=None,
            help="Minimum submition date of documents.",
        )
        parser.add_argument(
            "--from_hour",
            type=str,
            nargs="?",
            const=None,
            help="Minimum submition hour of documents.",
        )
        parser.add_argument(
            "--to_date",
            type=str,
            default=argparse.SUPPRESS,
            help="Maximum submition date of documents.",
        )
        parser.add_argument(
            "--to_hour",
            type=str,
            default=argparse.SUPPRESS,
            help="Maximum submition hour of documents.",
        )
        parser.add_argument(
            "--pdf",
            type=_bool,
            required=True,
            help="Set to `true` if you want to download the PDFs.",
        )
        parser.add_argument(
            "--response_dir",
            type=str,
            required=True,
            help="Target directory used to store fetched data.",
        )
        parser.add_argument(
            "--pdf_dir",
            type=str,
            nargs="?",
            const=None,
            help="Target directory used to store the PDFs.",
        )
        parser.add_argument(
            "--num_chunks",
            type=int,
            nargs="?",
            const=None,
            help="Number of semaphores for the PDF downloader.",
        )
        args, _ = parser.parse_known_args()
        return args


class MergerArgParse:
    """Argument parser used to build data for HuggingFace."""

    @classmethod
    def parse_known_args(cls):
        """Parses arguments.

        Returns
        -------
        args: Any
            Parsed arguments.
        """
        parser = argparse.ArgumentParser(description="Arguments used to merge data.")
        parser.add_argument(
            "--js_dir_path",
            type=str,
            required=True,
            help="Folder containing fetched data.",
        )
        parser.add_argument(
            "--txts_dir_path",
            type=str,
            required=True,
            help="Folder containing the txt files.",
        )
        parser.add_argument(
            "--output_dir_path",
            type=str,
            required=True,
            help="Final folder containing the processed data for HuggingFace.",
        )
        parser.add_argument(
            "--version",
            type=str,
            required=True,
            help="Version of the dump starting at '1.0'.",
        )
        args, _ = parser.parse_known_args()
        return args


class EnricherArgParse:
    """Argument parser used to enrish the HuggingFace dataset."""

    @classmethod
    def parse_known_args(cls):
        """Parses arguments.

        Returns
        -------
        args: Any
            Parsed arguments.
        """
        parser = argparse.ArgumentParser(
            description="""Download Sentencepiece and KenLM models for supported \
                languages."""
        )
        parser.add_argument(
            "--dataset_checkpoint",
            type=str,
            help="Name of the HuggingFace dataset to be processed.",
        )
        parser.add_argument(
            "--cache_dir_path",
            type=str,
            nargs="?",
            const=None,
            help="Path to the HuggingFace cache directory.",
        )
        parser.add_argument(
            "--dataset_config_path",
            type=str,
            default=None,
            help="Path to the txt file containing the dataset configs to process.",
        )
        parser.add_argument(
            "--download_models",
            type=_bool,
            default=True,
            help="Set to `true` if you want to download the KenLM models.",
        )
        parser.add_argument(
            "--kenlm_dir_path",
            type=str,
            help="Path to the directory containing the sentencepiece and kenlm models.",
        )
        parser.add_argument(
            "--num_proc",
            type=int,
            default=5,
            help="Number of processes to use for processing the dataset.",
        )
        parser.add_argument(
            "--batch_size",
            type=int,
            default=1000,
            help="Number of documents loaded per proc.",
        )
        parser.add_argument(
            "--output_dir_path",
            type=str,
            help="Path to the directory where the processed dataset will be saved.",
        )
        parser.add_argument(
            "--tokenizer_checkpoint",
            type=str,
            nargs="?",
            const=None,
            help="Name of the HuggingFace tokenizer model to be used.",
        )
        parser.add_argument(
            "--use_fast",
            type=_bool,
            nargs="?",
            const=False,
            help="Set to `true` if you want to use the Ruste-based tokenizer from HF.",
        )
        parser.add_argument(
            "--load_from_cache_file",
            type=_bool,
            nargs="?",
            const=False,
            help="Set to `true` if you if some of the enriching functions have been \
                altered.",
        )
        parser.add_argument(
            "--version",
            type=str,
            required=True,
            help="Version of the dump starting at '1.0'.",
        )
        args, _ = parser.parse_known_args()
        return args


class FilteringArgParse:
    """Argument parser used to filter the HuggingFace dataset."""

    @classmethod
    def parse_known_args(cls):
        """Parses arguments.

        Returns
        -------
        args: Any
            Parsed arguments.
        """
        parser = argparse.ArgumentParser(
            description="Argument used to filter the dataset."
        )
        parser.add_argument(
            "--dataset_checkpoint",
            type=str,
            help="Name of the HuggingFace dataset to be processed.",
        )
        parser.add_argument(
            "--cache_dir_path",
            type=str,
            nargs="?",
            const=None,
            help="Path to the HuggingFace cache directory.",
        )
        parser.add_argument(
            "--dataset_config_path",
            type=str,
            default=None,
            help="Path to the txt file containing the dataset configs to process.",
        )
        parser.add_argument(
            "--num_proc",
            type=int,
            default=5,
            help="Number of processes to use for processing the dataset.",
        )
        parser.add_argument(
            "--batch_size",
            type=int,
            default=1000,
            help="Number of documents loaded per proc.",
        )
        parser.add_argument(
            "--output_dir_path",
            type=str,
            help="Path to the directory where the processed dataset will be saved.",
        )
        parser.add_argument(
            "--load_from_cache_file",
            type=_bool,
            nargs="?",
            const=False,
            help="Set to `true` if you if some of the enriching functions have been \
                altered.",
        )
        parser.add_argument(
            "--version",
            type=str,
            required=True,
            help="Version of the dump starting at '1.0'.",
        )
        args, _ = parser.parse_known_args()
        return args


class ExperimentsArgParse:
    """Argument parser used to enrish the HuggingFace dataset."""

    @classmethod
    def parse_known_args(cls):
        """Parses arguments.

        Returns
        -------
        args: Any
            Parsed arguments.
        """
        parser = argparse.ArgumentParser(
            description="""Aggregate the number of documents and tokens per language \
                and per domain."""
        )
        parser.add_argument(
            "--dataset_checkpoint",
            type=str,
            help="Name of the HuggingFace dataset to be processed.",
        )
        parser.add_argument(
            "--dataset_config_path",
            type=str,
            default=None,
            help="Path to the txt file containing the dataset configs to process.",
        )
        parser.add_argument(
            "--output_dir_path",
            type=str,
            help="Path to the directory where the dataset's statistics will be saved.",
        )
        parser.add_argument(
            "--cache_dir_path",
            type=str,
            nargs="?",
            const=None,
            help="Path to the HuggingFace cache directory.",
        )
        parser.add_argument(
            "--num_proc",
            type=int,
            default=5,
            help="Number of processes to use for processing the dataset.",
        )
        parser.add_argument(
            "--batch_size",
            type=int,
            default=1000,
            help="Number of documents loaded per proc.",
        )
        parser.add_argument(
            "--count_raw_tokens",
            type=_bool,
            required=True,
            help="Set to `true` if the dataset has a `token_count` attribute.",
        )
        args, _ = parser.parse_known_args()
        return args
