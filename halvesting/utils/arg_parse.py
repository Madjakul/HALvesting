# utils/arg_parse.py

import argparse


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
            default=argparse.SUPPRESS,
            help="Date of the last update",
        )
        parser.add_argument(
            "--from_hour",
            type=str,
            default=argparse.SUPPRESS,
            help="Hour of the last update",
        )
        parser.add_argument(
            "--to_date",
            type=str,
            default=argparse.SUPPRESS,
            help="Date of the last document submitted.",
        )
        parser.add_argument(
            "--to_hour",
            type=str,
            default=argparse.SUPPRESS,
            help="Hour of the last document submitted.",
        )
        parser.add_argument(
            "--pdf",
            action="store_true",
            help="If you want PDFs to be downloaded on the fly or not.",
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
            help="Target directory used to store PDFs.",
        )
        parser.add_argument(
            "--num_chunks",
            type=int,
            nargs="?",
            const=None,
            help="Number of semaphores.",
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
        parser = argparse.ArgumentParser(description="Arguments used to fetch data.")
        parser.add_argument(
            "--js_folder",
            type=str,
            required=True,
            help="Folder containing fetched data.",
        )
        parser.add_argument(
            "--txt_folder",
            type=str,
            required=True,
            help="Folder containing the txt files.",
        )
        parser.add_argument(
            "--hf_folder",
            type=str,
            required=True,
            help="Final folder containing the processed data for HuggingFace.",
        )
        args, _ = parser.parse_known_args()
        return args


class EnrisherArgParse:
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
            description="Download Sentencepiece and KenLM models for supported languages."
        )
        parser.add_argument(
            "--output_dir_path",
            type=str,
            default=None,
            help="Output directory path to save models.",
        )
        parser.add_argument(
            "--langs",
            type=str,
            default="all",
            help="Languages to download models for. Default is all supported languages.",
        )
        parser.add_argument(
            "--dataset_name",
            type=str,
            help="Name of the dataset to be processed.",
        )
        parser.add_argument(
            "--dataset_config_names",
            type=str,
            default=None,
            help="Comma-separated list of dataset config names to be processed.",
        )
        parser.add_argument(
            "--kenlm_dir_path",  # Change to output dir
            type=str,
            help="Path to the directory containing the sentencepiece and kenlm models.",
        )
        parser.add_argument(
            "--fasttext_model_file",
            type=str,
            help="Path to the fasttext model file.",
        )
        parser.add_argument(
            "--hf_model_name",
            type=str,
            default="google/mt5-small",
            help="Name of the Hugging Face model to be used for tokenization.",
        )
        parser.add_argument(
            "--output_dir_path",  # change to dataset_dir_path
            type=str,
            help="Path to the directory where the processed dataset will be saved.",
        )
        parser.add_argument(
            "--num_proc",
            type=int,
            default=1,
            help="Number of processes to use for processing the dataset.",
        )
        args, _ = parser.parse_known_args()
        return args
