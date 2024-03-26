"""Download Sentencepiece and KenLM models for supported languages.

Usage:
    python download_sentencepiece_kenlm_models.py --output_dir_path /tmp/

All Sentencepiece and KenLM language models will be saved under /tmp.
"""

import argparse
import os

import pandas as pd
from huggingface_hub import hf_hub_download
from tqdm import tqdm


_LANG_MAP = {
    "Afrikaans": "af",
    "Albanian": "sq",
    "Amharic": "am",
    "Arabic": "ar",
    "Aragonese": "an",
    "Armenian": "hy",
    "Assamese": "as",
    "Asturian": "ast",
    "Avaric": "av",
    "Azerbaijani": "az",
    "Bangla": "bn",
    "Bashkir": "ba",
    "Basque": "eu",
    "Bavarian": "bar",
    "Belarusian": "be",
    "Bihari languages": "bh",
    "Bishnupriya": "bpy",
    "Bosnian": "bs",
    "Breton": "br",
    "Bulgarian": "bg",
    "Burmese": "my",
    "Cantonese": "yue",
    "Catalan": "ca",
    "Cebuano": "ceb",
    "Central Bikol": "bcl",
    "Central Kurdish": "ckb",
    "Chavacano": "cbk",
    "Chechen": "ce",
    "Chinese": "zh",
    "Chuvash": "cv",
    "Cornish": "kw",
    "Corsican": "co",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Divehi": "dv",
    "Dutch": "nl",
    "Eastern Mari": "mhr",
    "Egyptian Arabic": "arz",
    "Emiliano-Romagnol": "eml",
    "English": "en",
    "Erzya": "myv",
    "Esperanto": "eo",
    "Estonian": "et",
    "Filipino": "tl",
    "Finnish": "fi",
    "French": "fr",
    "Galician": "gl",
    "Georgian": "ka",
    "German": "de",
    "Goan Konkani": "gom",
    "Greek": "el",
    "Guarani": "gn",
    "Gujarati": "gu",
    "Haitian Creole": "ht",
    "Hebrew": "he",
    "Hindi": "hi",
    "Hungarian": "hu",
    "Icelandic": "is",
    "Ido": "io",
    "Iloko": "ilo",
    "Indonesian": "id",
    "Interlingua": "ia",
    "Interlingue": "ie",
    "Irish": "ga",
    "Italian": "it",
    "Japanese": "ja",
    "Javanese": "jv",
    "Kalmyk": "xal",
    "Kannada": "kn",
    "Karachay-Balkar": "krc",
    "Kazakh": "kk",
    "Khmer": "km",
    "Komi": "kv",
    "Korean": "ko",
    "Kurdish": "ku",
    "Kyrgyz": "ky",
    "Lao": "lo",
    "Latin": "la",
    "Latvian": "lv",
    "Lezghian": "lez",
    "Limburgish": "li",
    "Lithuanian": "lt",
    "Lojban": "jbo",
    "Lombard": "lmo",
    "Low German": "nds",
    "Lower Sorbian": "dsb",
    "Luxembourgish": "lb",
    "Macedonian": "mk",
    "Maithili": "mai",
    "Malagasy": "mg",
    "Malay": "ms",
    "Malayalam": "ml",
    "Maltese": "mt",
    "Marathi": "mr",
    "Mazanderani": "mzn",
    "Minangkabau": "min",
    "Mingrelian": "xmf",
    "Mirandese": "mwl",
    "Mongolian": "mn",
    "Nahuatl languages": "nah",
    "Neapolitan": "nap",
    "Nepali": "ne",
    "Newari": "new",
    "Northern Frisian": "frr",
    "Northern Luri": "lrc",
    "Norwegian": "no",
    "Norwegian Nynorsk": "nn",
    "Occitan": "oc",
    "Odia": "or",
    "Ossetic": "os",
    "Pampanga": "pam",
    "Pashto": "ps",
    "Persian": "fa",
    "Piedmontese": "pms",
    "Polish": "pl",
    "Portuguese": "pt",
    "Punjabi": "pa",
    "Quechua": "qu",
    "Romanian": "ro",
    "Romansh": "rm",
    "Russia Buriat": "bxr",
    "Russian": "ru",
    "Rusyn": "rue",
    "Sakha": "sah",
    "Sanskrit": "sa",
    "Scottish Gaelic": "gd",
    "Serbian": "sr",
    "Serbian (Latin)": "sh",
    "Sicilian": "scn",
    "Sindhi": "sd",
    "Sinhala": "si",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Somali": "so",
    "South Azerbaijani": "azb",
    "Spanish": "es",
    "Sundanese": "su",
    "Swahili": "sw",
    "Swedish": "sv",
    "Swiss German": "als",
    "Tajik": "tg",
    "Tamil": "ta",
    "Tatar": "tt",
    "Telugu": "te",
    "Tetum": "tet",
    "Thai": "th",
    "Tibetan": "bo",
    "Turkish": "tr",
    "Turkmen": "tk",
    "Tuvinian": "tyv",
    "Ukrainian": "uk",
    "Upper Sorbian": "hsb",
    "Urdu": "ur",
    "Uyghur": "ug",
    "Uzbek": "uz",
    "Venetian": "vec",
    "Vietnamese": "vi",
    "Volapuk": "vo",
    "Walloon": "wa",
    "Waray": "war",
    "Welsh": "cy",
    "West Flemish": "vls",
    "Western Frisian": "fy",
    "Western Mari": "mrj",
    "Western Panjabi": "pnb",
    "Wu Chinese": "wuu",
    "Yiddish": "yi",
    "Yoruba": "yo",
}
_LANG_MAP_INV = {v: k for k, v in _LANG_MAP.items()}
_LANGS = [
    "ar",
    "az",
    "bg",
    "bo",
    "br",
    "bs",
    "ca",
    "co",
    "cs",
    "da",
    "de",
    "el",
    "en",
    "eo",
    "es",
    "et",
    "eu",
    "fa",
    "fi",
    "fr",
    "gl",
    "gn",
    "he",
    "hi",
    "hr",
    "hu",
    "hy",
    "id",
    "ie",
    "it",
    "ja",
    "kk",
    "ko",
    "la",
    "lt",
    "mk",
    "mr",
    "ms",
    "nl",
    "no",
    "oc",
    "pl",
    "pt",
    "ro",
    "ru",
    "sk",
    "sl",
    "sq",
    "sr",
    "sv",
    "sw",
    "ta",
    "tet",
    "th",
    "tk",
    "tl",
    "tr",
    "uk",
    "vi",
    "zh",
]
_LANGS_ID = [
    {
        "lang": _LANG_MAP_INV[v],
        "dataset_id": v,
        "stopwords_id": v,
        "flagged_words_id": v,
        "fasttext_id": v,
        "sentencepiece_id": v,
        "kenlm_id": v,
    }
    for v in _LANGS
]
LANGS_ID = pd.DataFrame(_LANGS_ID)
HF_TOKEN = os.getenv("HF_TOKEN")


def download_sentencepiece_kenlm_models(output_dir_path: str, langs: str) -> None:

    if output_dir_path is None:
        DATA_PREP_WORKING_DIR = os.getenv("DATA_PREP_WORKING_DIR")

        assert (
            DATA_PREP_WORKING_DIR is not None
        ), "Please specify a valid output directory path by setting the environment variable 'DATA_PREP_WORKING_DIR'"

        output_dir_path = os.path.join(
            DATA_PREP_WORKING_DIR, "sentencepiece_kenlm_models"
        )

        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)

    supported_sentencepiece_langs = langs_id["sentencepiece_id"].dropna().unique()
    supported_kenlm_langs = langs_id["kenlm_id"].dropna().unique()

    if langs == "all":
        selected_sentencepiece_langs = supported_sentencepiece_langs
        selected_kenlm_langs = supported_kenlm_langs
    else:
        langs = langs.split(",")
        # check if all languages are supported
        assert all(
            lang in supported_sentencepiece_langs for lang in langs
        ), "Please specify a valid language or use 'all' to download all supported languages."
        assert all(
            lang in supported_kenlm_langs for lang in langs
        ), "Please specify a valid language or use 'all' to download all supported languages."

        selected_kenlm_langs = langs
        selected_sentencepiece_langs = langs

    for lang in tqdm(selected_sentencepiece_langs):
        try:
            # output_sentencepiece = subprocess.check_output(
            #     f"wget -q -nv https://huggingface.co/edugp/kenlm/resolve/main/wikipedia/{lang}.sp.model -P {output_dir_path}",  # http://dl.fbaipublicfiles.com/cc_net/lm/{lang}.sp.model for FB models
            #     shell=True,
            # )
            # print(
            #     f'wget -q -nv --header="Authorization: Bearer {HF_TOKEN}" https://huggingface.co/uonlp/kenlm/blob/main/wikipedia_20230501/{lang}.sp.model -P {output_dir_path}'
            # )
            # output_sentencepiece = subprocess.check_output(
            #     f'wget -q -nv --header="Authorization: Bearer {HF_TOKEN}" https://huggingface.co/uonlp/kenlm/blob/main/wikipedia_20230501/{lang}.sp.model -P {output_dir_path}',  # http://dl.fbaipublicfiles.com/cc_net/lm/{lang}.sp.model for FB models
            #     shell=True,
            # )
            hf_hub_download(
                repo_id="uonlp/kenlm",
                filename=f"wikipedia_20230501/{lang}.sp.model",
                local_dir=output_dir_path,
                local_dir_use_symlinks=False,
            )
        # exit(0)
        except:
            print(
                f"Warning: Download failed for Sentencepiece model for language {lang}."
            )

    for lang in tqdm(selected_kenlm_langs):
        try:
            # output_kenlm = subprocess.check_output(
            #     f'wget -q -nv --header="Authorization: Bearer {HF_TOKEN}" https://huggingface.co/uonlp/kenlm/blob/main/wikipedia_20230501/{lang}.arpa.bin -P {output_dir_path}',  # http://dl.fbaipublicfiles.com/cc_net/lm/{lang}.arpa.bin for FB models
            #     shell=True,
            # )
            hf_hub_download(
                repo_id="uonlp/kenlm",
                filename=f"wikipedia_20230501/{lang}.arpa.bin",
                local_dir=output_dir_path,
                local_dir_use_symlinks=False,
            )
        except:
            print(f"Warning: Download failed for KenLM model for language {lang}.")


if __name__ == "__main__":
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

    args = parser.parse_args()

    download_sentencepiece_kenlm_models(
        output_dir_path=args.output_dir_path, langs=args.langs
    )
