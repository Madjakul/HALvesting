# halvesting/utils/data/postprocessing.py

import re
import string
import unicodedata
from typing import Dict

from nltk.tokenize import WordPunctTokenizer
from transformers import AutoTokenizer

PRECISION = 2
TRANSLATION_TABLE_PUNCTUATION = str.maketrans("", "", string.punctuation)
NON_PRINTING_CHAR_RE: re.Pattern = re.compile(
    f"[{''.join(map(chr, list(range(0,32)) + list(range(127,160))))}]"
)
DIGITS_RE: re.Pattern = re.compile(r"\d")
UNICODE_PUNCTUATION: Dict[str, str] = {
    "，": ",",
    "。": ".",
    "、": ",",
    "„": '"',
    "”": '"',
    "“": '"',
    "«": '"',
    "»": '"',
    "１": '"',
    "」": '"',
    "「": '"',
    "《": '"',
    "》": '"',
    "´": "'",
    "∶": ":",
    "：": ":",
    "？": "?",
    "！": "!",
    "（": "(",
    "）": ")",
    "；": ";",
    "–": "-",
    "—": " ",
    "～": "~",
    "’": "'",
    "…": "...",
    "━": "-",
    "〈": "<",
    "〉": ">",
    "【": "[",
    "】": "]",
    "％": "%",
    "►": "-",
}


class Postprocessing:
    """Class for postprocessing text data.

    Parameters
    ----------
    text : str
        The raw text to be processed.

    Attributes
    ----------
    tokenizer : AutoTokenizer
        Tokenizer for tokenizing text.
    word_tokenizer : WordPunctTokenizer
        Tokenizer for tokenizing words.
    """

    tokenizer = AutoTokenizer.from_pretrained("google/mt5-small")
    word_tokenizer = WordPunctTokenizer()

    def __init__(self, text: str, **kwargs):
        self.raw_content = text
        self.raw_words = tuple(self.word_tokenizer.tokenize(self.raw_content))
        self.num_raw_words = len(self.raw_words)
        self.normalized_content = self._normalize(text)
        self.normalized_words = self.normalized_content.split()
        self.num_normalized_words = len(self.normalized_words)
        self.__dict__.update(kwargs)

    def count_tokens(self, text: str):
        """Count the number of tokens in the text.

        Parameters
        ----------
        text : str
            The text to count tokens from.

        Returns
        -------
        lenght: int
            The total number of tokens in the text.
        """
        # split the text into tokens and chunk into batches of 512 tokens
        text_split = text.split()
        length = 0
        for i in range(0, len(text_split), 512):
            length += len(
                self.tokenizer.encode(
                    " ".join(text_split[i : i + 512]), add_special_tokens=False
                ).tokens
            )

        return length

    def rps_doc_frac_all_caps_words(self):
        """Calculate the fraction of words in all caps in the raw content.

        Returns
        -------
        score: float
            The fraction of words in all caps.
        """
        if self.num_raw_words == 0:
            return None

        score = float(sum(map(str.isupper, self.raw_words))) / self.num_raw_words
        score = round(score, PRECISION)
        return score

    def rps_doc_frac_no_alph_words(self):
        """Calculate the fraction of words with no alphabetical characters in
        the raw content.

        Returns
        -------
        score: float
            The fraction of words with no alphabetical characters.
        """
        alph_regex = re.compile(r"[a-zA-Z]")

        if self.num_raw_words == 0:
            return None

        num_words_with_alpha = float(
            sum(int(alph_regex.search(word) is not None) for word in self.raw_words)
        )

        score = 1.0 - num_words_with_alpha / self.num_raw_words
        score = round(score, PRECISION)
        return score

    def rps_doc_lorem_ipsum(self):
        """Calculate the ratio of occurrences of 'lorem ipsum' to total
        characters in the normalized content.

        Returns
        -------
        score: float
            The ratio of occurrences of 'lorem ipsum' to total characters.
        """
        search_text = "lorem ipsum"
        search_regex = re.compile(r"lorem ipsum", re.IGNORECASE)

        if len(self.normalized_content) == 0:
            return 0.0

        if search_text not in self.normalized_content:
            return 0.0

        num_occurences = len(search_regex.findall(self.normalized_content))

        score = float(num_occurences) / len(self.normalized_content)
        score = round(score, PRECISION)

        return score

    def rps_doc_mean_word_length(self):
        """Calculate the mean length of words in the normalized content.

        Returns
        -------
        score: float
            The mean length of words in the normalized content.
        """
        if self.num_normalized_words == 0:
            return None

        num_chars = float(sum(map(len, self.normalized_words)))
        score = num_chars / self.num_normalized_words
        score = round(score, PRECISION)
        return score

    def rps_doc_symbol_to_word_ratio(self):
        """Calculate the ratio of symbols to words in the raw content.

        Returns
        -------
        score: float
            The ratio of symbols to words.
        """
        SYMBOLS = ("#", "...", "…")

        num_words = self.num_raw_words

        if num_words == 0:
            return None

        # count the number of symbols in the content
        num_symbols = float(sum(self.raw_content.count(x) for x in SYMBOLS))

        score = num_symbols / num_words
        score = round(score, PRECISION)
        return score

    def rps_doc_frac_unique_words(self):
        """Calculate the fraction of unique words in the normalized content.

        Returns
        -------
        score: float
            The fraction of unique words.
        """
        num_words = self.num_normalized_words

        if num_words == 0:
            return None

        score = float(len(set(self.normalized_words))) / num_words
        score = round(score, PRECISION)
        return score

    def rps_doc_word_count(self):
        """Return the number of words in the normalized content.

        Returns
        -------
        int
            The number of words in the normalized content.
        """
        return self.num_normalized_words

    @staticmethod
    def _normalize(text: str):
        """Normalize the text by lowercasing and removing punctuation.

        Parameters
        ----------
        text : str
            The text to be normalized.

        Returns
        -------
        text: str
            The normalized text.
        """
        # remove punctuation
        text = text.translate(TRANSLATION_TABLE_PUNCTUATION)
        # lowercase
        text = text.lower()
        # Remove leading, trailing and extra white spaces
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        # NFD unicode normalization
        text = unicodedata.normalize("NFD", text)

        return text
