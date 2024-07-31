# halvesting/utils/data/postprocessing.py

import json
import logging
import math
import os
import re
import string
import unicodedata
from collections import Counter

import ftfy
from kenlm import Model
from nltk.tokenize import WordPunctTokenizer
from sentencepiece import SentencePieceProcessor
from transformers import AutoTokenizer

from halvesting.utils import DATA_ROOT, tokenize_

_PRECISION = 2
_TRANSLATION_TABLE_PUNCTUATION = str.maketrans("", "", string.punctuation)
_DIGITS_RE: re.Pattern = re.compile(r"\d")
with open(os.path.join(DATA_ROOT, "stopwords.json"), "r", encoding="utf-8") as jsf:
    _STOPWORDS = json.load(jsf)
_COVER_TEXT_FR = (
    "L'archive ouverte pluridisciplinaire HAL, est destinée au dépôt et à la diffusion "
    "de documents scientifiques de niveau recherche, publiés ou non, émanant des "
    "établissements d'enseignement et de recherche français ou étrangers, des "
    "laboratoires publics ou privés."
)
_COVER_TEXT_FR_2 = re.compile(
    "et à la diffusion de documents scientifiques de niveau "
    "recherche, publiés ou non, émanant des établissements d'enseignement et de "
    "recherche français ou étrangers, des laboratoires publics ou privés."
)
_COVER_TEXT_EN = (
    "HAL is a multi-disciplinary open access archive for the deposit "
    "and dissemination of scientific research documents, whether they are published "
    "or not. The documents may come from teaching and research institutions in France "
    "or abroad, or from public or private research centers."
)
_COVER_TEXT_EN_2 = (
    "from teaching and research institutions in France or abroad, or from public or "
    "private research centers."
)


class Postprocessing:
    """Class used to postprocess text data. Contains functions to clean the
    texts, normalize them before running some statistics on them.

    Notes
    -----
    Most of the functions used here come from the **togethercomputer**'s implementation
    computed when building RedPajama [1]_ . The original functions where introduced by
    Raffel et al [2]_ , Penedo et al [3]_ and Rae et al [4]_ .

    Warnings
    --------
    Most of the methods involving computing the number of words of a text won't work as
    expected on Chinese and Japanese text as they often don't use blank spaces to
    separate "words".

    Parameters
    ----------
    text : str
        The raw text to be processed.
    lang: str
        ISO-636 language code of the text retrieved from HAL.

    Attributes
    ----------
    tokenizer : transformers.AutoTokenizer
        **HuggingFace** tokenizer used to tokenize the raw content. By default, the
        tokenizer used is "google/mt5-base". The slow tokenizer from **HF** is the
        preferred one as `the fast one can hang for a while on long sequences`_ .
    word_tokenizer : nltk.tokenize.WordPunctTokenizer
        Word-level tokenizer used to compute statistics.
    lang: str
        ISO-636 language code of the text retrieved from HAL.
    raw_content: str
        Input text somwhat fixed. The fixing process consisting in some basic functions
        does not solve the most severe encoding issues.
    raw_words: Tuple[str]
        List of words in `self.raw_content` returned by ``self.word_tokenizer``.
    num_raw_words: int
        Number of words in ``self.raw_words``.
    raw_lines: Tuple[str]
        ``self.raw_content`` separated by lines.
    num_raw_lines: int
        Length of ``self.raw_lines``.
    normalized_content: str
        ``raw_content`` normalized. All characers are lower cased and numbers are
        remapped to 0.
    normalized_words: Tuple[str]
        List of words in ``self.normalized_content`` returned by
        ``self.word_tokenizer``.
    num_normalized_words: int
        Length of `self.normalized_words`.

    Examples
    --------
    >>> from halvesting.utils.data import Postprocessing
    >>> text = "Lorem Ipsum dolor sit amet,"
    >>> document = Postprocessing(text=text, lang="en")
    >>> document.rps_doc_frac_all_caps_words()
    0.0


    ..  [1] RedPajama: An Open Dataset for Training Large Language Models. Together
        Computer, Oct. 2023, https://github.com/togethercomputer/RedPajama-Data.
    ..  [2] Raffel, Colin, et al. “Exploring the Limits of Transfer Learning with a
        Unified Text-to-Text Transformer.” The Journal of Machine Learning Research,
        vol. 21, no. 1, Jan. 2020, p. 140:5485-140:5551.
    ..  [3] Penedo, Guilherme, et al. “The RefinedWeb Dataset for Falcon LLM:
        Outperforming Curated Corpora with Web Data Only.” Advances in Neural
        Information Processing Systems, vol. 36, Dec. 2023, pp. 79155–72.
    ..  [4] Rae, Jack W., et al. Scaling Language Models: Methods, Analysis & Insights
        from Training Gopher. arXiv:2112.11446, arXiv, 21 Jan. 2022. arXiv.org,
        https://doi.org/10.48550/arXiv.2112.11446.
    ..  _`the fast one can hang for a while on long sequences`: https://github.com/huggingface/transformers/issues/25873
    """

    tokenizer = AutoTokenizer.from_pretrained("google/mt5-base", use_fast=False)
    word_tokenizer = WordPunctTokenizer()

    def __init__(self, text: str, lang: str, **kwargs):
        self.lang = lang
        self.raw_content = self.fix_text(text)
        self.raw_words = tuple(self.word_tokenizer.tokenize(self.raw_content))
        self.num_raw_words = len(self.raw_words)
        self.raw_lines = tuple(self.raw_content.split("\n"))
        self.num_raw_lines = len(self.raw_lines)
        self.normalized_content = self._normalize(text)
        self.normalized_words = tuple(
            self.word_tokenizer.tokenize(self.normalized_content)
        )
        self.num_normalized_words = len(self.normalized_words)
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        self.__dict__.update(kwargs)

    def count_tokens(self):
        """Tokenizes `self.raw_content` and count the number of tokens without
        the special ones.

        Returns
        -------
        int
            The total number of tokens in the text.
        """
        if self.num_raw_words == 0:
            return None

        return len(self.tokenizer.encode(self.raw_content, add_special_tokens=False))

    def rps_doc_frac_all_caps_words(self):
        """Calculates the fraction of words in all caps in the raw content.

        Returns
        -------
        score: float
            The fraction of words in all caps.
        """
        if self.num_raw_words == 0:
            return None

        score = sum(map(str.isupper, self.raw_words)) / self.num_raw_words
        score = round(score, _PRECISION)
        return score

    def rps_doc_frac_lines_end_with_ellipsis(self):
        """Calculates the fraction of lines that end with an ellipsis, where an
        ellipsis is defined as either "..." or "…".

        Returns
        -------
        score: float
            The fraction of lines ending with ellipsis.
        """
        ellipsis_symbols = ("...", "…")

        if self.num_raw_lines == 0:
            return None

        score = (
            sum(map(lambda x: x.endswith(ellipsis_symbols), self.raw_lines))
            / self.num_raw_lines
        )
        score = round(score, _PRECISION)
        return score

    def rps_doc_frac_no_alph_words(self):
        """Calculates the fraction of words with no alphabetical characters in
        the raw content.

        Returns
        -------
        score: float
            The fraction of words with no alphabetical characters.
        """
        if self.num_raw_words == 0:
            return None

        score = 1.0 - sum(map(str.isalpha, self.raw_words)) / self.num_raw_words
        score = round(score, _PRECISION)
        return score

    def rps_doc_lorem_ipsum(self):
        """Calculates the ratio of occurrences of 'lorem ipsum' to total
        characters in the normalized content.

        Returns
        -------
        score: float
            The ratio of occurrences of 'lorem ipsum' to total characters.
        """
        search_text = "lorem ipsum"
        search_regex = re.compile(r"lorem ipsum", re.IGNORECASE)

        if len(self.normalized_content) == 0:
            return None

        if search_text not in self.normalized_content:
            return 0.0

        num_occurences = len(search_regex.findall(self.normalized_content))

        score = num_occurences / len(self.normalized_content)
        score = round(score, _PRECISION)

        return score

    def rps_doc_mean_word_length(self):
        """Calculates the mean length of words in the normalized content.

        Returns
        -------
        score: float
            The mean length of words in the normalized content.
        """
        if self.num_normalized_words == 0:
            return None

        num_chars = sum(map(len, self.normalized_words))
        score = num_chars / self.num_normalized_words
        score = round(score, _PRECISION)
        return score

    def rps_doc_stop_word_fraction(self):
        """Calculates the ratio between the number of stop words and the number
        of words in the document.

        Notes
        -----
        The stop words are fetched from `stopwords-json`_ .

        Returns
        -------
        score: float
            The ratio beetwen the stop words and the total number of words in
            `self.normalized_words`.


        ..  _`stopwords-json`: https://github.com/6/stopwords-json/tree/master
        """
        try:
            stop_words = _STOPWORDS[self.lang]
        except KeyError:
            logging.error(f"No stop words for language {self.lang}.")
            return None

        if self.num_normalized_words == 0:
            return None

        num_stop_words = sum(map(lambda w: w in stop_words, self.normalized_words))

        score = float(num_stop_words) / self.num_normalized_words
        score = round(score, _PRECISION)

        return score

    def rps_doc_symbol_to_word_ratio(self):
        """Calculates the ratio of symbols to words in the raw content.

        Returns
        -------
        score: float
            The ratio of symbols to words.
        """
        symbols = ("#", "...", "…")

        if self.num_raw_words == 0:
            return None

        # count the number of symbols in the content
        num_symbols = sum(self.raw_content.count(x) for x in symbols)

        score = num_symbols / self.num_raw_words
        score = round(score, _PRECISION)
        return score

    def rps_doc_frac_unique_words(self):
        """Calculates the fraction of unique words in the normalized content.

        Returns
        -------
        score: float
            The fraction of unique words.
        """
        if self.num_normalized_words == 0:
            return None

        score = len(set(self.normalized_words)) / self.num_normalized_words
        score = round(score, _PRECISION)
        return score

    def rps_doc_unigram_entropy(self):  # noqa
        r"""Calculates the entropy of the unigram distribution of the content.

        Notes
        -----
        This measures the diversity of the content and is computed using

        ..  math::

            \sum_{S}(\frac{-\vert w\vert}{\vert S \vert} * log(\frac{\vert w \vert}{\vert S \vert}))

        where the sum is taken over over counts of unique words in the noramlized
        (punctuation removed, lowercased) content :math:`S`.

        Returns
        -------
        score: float
            The entropy of the unigram distribution of content.
        """
        if self.num_normalized_words == 0:
            return None

        counter = Counter(self.normalized_words)

        # calculate the entropy of the unigram distribution
        total = sum(counter.values())
        entropy = sum(
            map(
                lambda x: -x / total * math.log(x / total) if x > 0 else 0.0,
                counter.values(),
            )
        )

        score = round(entropy, _PRECISION)
        return score

    def rps_doc_word_count(self):
        """Returns the number of words in the normalized content.

        Returns
        -------
        int
            The number of words in the normalized content.
        """
        return self.num_normalized_words

    def doc_frac_lines_ending_with_terminal_punctution_mark(self):
        """Calculates the ratio of lines with a terminal punctuation mark. A
        terminal punctation mark is defined as one of the following: ".", "!",
        "?", "”",  "。".

        Returns
        -------
        score: float
            The ratio of lines ending with a punctuation mark.
        """
        terminal_punctuation_marks = (".", "!", "?", "”", '"', "。")

        if self.num_raw_lines == 0:
            return None

        score = (
            sum(map(lambda x: x.endswith(terminal_punctuation_marks), self.raw_lines))
            / self.num_raw_lines
        )
        score = round(score, _PRECISION)
        return score

    def rps_lines_frac_start_with_bulletpoint(self):
        r"""Calculates the ratio of lines that start with a bullet point symbol.

        The following set of unicodes are considered a bullet point:
        \u2022 (bullet point), \u2023 (triangular bullet point), \u25B6 (black
        right pointing triangle), \u25C0 (black left pointing triangle),
        \u25E6 (white bullet point), \u25A0 (black square), \u25A1 (white
        square), \u25AA (black small square), \u25AB (white small square),
        \u2013 (en dash).

        Returns
        -------
        score: float
            The ratio of lines that start with a bullet point symbol.
        """
        if self.num_raw_lines == 0:
            return None

        bullet_point_symbols = (
            "\u2022",  # bullet point
            "\u2023",  # triangular bullet point
            "\u25B6",  # black right pointing triangle
            "\u25C0",  # black left pointing triangle
            "\u25E6",  # white bullet point
            "\u25A0",  # black square
            "\u25A1",  # white square
            "\u25AA",  # black small square
            "\u25AB",  # white small square
            "\u2013",  # en dash
        )
        score = (
            sum(map(lambda x: x.startswith(bullet_point_symbols), self.raw_lines))
            / self.num_raw_lines
        )
        score = round(score, _PRECISION)
        return score

    def rps_doc_num_sentences(self):
        """The number of sentences in the content. This is calculated using the
        regex r"\b[^.!?。]+[.!?。]*".

        Returns
        -------
        score: int
            The number of sentences in the raw content.
        """
        if len(self.raw_content) == 0:
            return None

        sent_pattern = re.compile(r"\b[^.!?。]+[.!?。]*", flags=re.UNICODE)
        score = len(sent_pattern.findall(self.raw_content))
        return score

    def rps_frac_chars_in_dupe_ngrams(self, n: int):
        """Calculates the fraction of characters in duplicate word N-grams.
        This operates on the lower-cased, punctation removed content. The
        function also ensures that characters in overlapping ngrams are only
        counted once.

        Parameters
        ----------
        n: int
            Size of n-grams.

        Returns
        -------
        score: float
            The fraction of n-grams repeted throughout the document.
        """
        if self.num_normalized_words < n:
            return 0.0

        ngrams = [
            self.normalized_content[i : i + n]
            for i in range(len(self.normalized_content) - n + 1)
        ]
        ngrams_size = len(ngrams)
        ngrams_count = Counter(ngrams)
        dedup_size = sum(count for count in ngrams_count.values() if count > 1)
        score = dedup_size / ngrams_size
        score = round(score, _PRECISION)
        return score

    def compute_perplexity(
        self,
        sentencepiece_model: SentencePieceProcessor,
        kenlm_model: Model,
    ):
        """Computes the perplexity of the normalized text.

        Parameters
        ----------
        sentencepiece_model: sentencepiece.SentencePieceProcessor
            The **sentencepiece** tokenizer used to encode text for the `kenlm_model`.
        kenlm_model: kenlm.Model
            Language model used to compute the perplexity.

        Returns
        -------
        pp_score: float
            The average perplexity score per line.
        """
        doc_log_score, doc_length = 0, 0
        for line in self.normalized_content.split("\n"):
            if not line:
                continue
            line = tokenize_(line, sentencepiece_model)
            log_score = kenlm_model.score(line)
            length = len(line.split()) + 1
            doc_log_score += log_score
            doc_length += length
        pp_score = 10.0 ** (-doc_log_score / doc_length)
        pp_score = round(pp_score, 1)
        return pp_score

    @staticmethod
    def _normalize(text: str):
        """Normalizes the text by lowercasing, removing punctuation and
        replacing number with zeros.

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
        text = text.translate(_TRANSLATION_TABLE_PUNCTUATION)
        # lowercase
        text = text.lower()
        # Remove leading, trailing and extra white spaces
        text = re.sub(r"\s+", " ", text)
        # NFD unicode normalization
        text = unicodedata.normalize("NFD", text)
        text = Postprocessing.replace_digits_with_zeros(text)
        return text

    @staticmethod
    def fix_text(text: str):
        """Removes some artifacts from the PDF conversion to plain text and
        ensures a proper utf-8 encoding with text aligned from left to right.

        Parameters
        ----------
        text: str
            The text to fix.

        Returns
        -------
        text: str
            The fixed text.
        """
        text = re.sub(_COVER_TEXT_FR, " ", text)
        text = re.sub(_COVER_TEXT_FR_2, " ", text)
        text = re.sub(_COVER_TEXT_EN, " ", text)
        text = re.sub(_COVER_TEXT_EN_2, " ", text)
        text = Postprocessing.remove_extra_newlines(text)
        # Aligning text from left to right
        text = text.replace("\u202b", "").replace("\u202c", "")
        # Fix some of the encodning problems
        text = ftfy.fix_text(text)
        return text

    @staticmethod
    def remove_extra_newlines(text: str):
        """Removes extra new lines, keeping at most two consecutive new lines
        in the text if needed.

        Parameters
        ----------
        text: str
            The text to process.

        Returns
        -------
        text: str
            The processed text.
        """
        text = text.strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

    @staticmethod
    def replace_digits_with_zeros(text: str, digits_re: re.Pattern = _DIGITS_RE):
        """Replaces all the numbers with zeros.

        Parameters
        ----------
        text: str
            The text to process.
        digits_re: re.Pattern
            Regular expression used to catch digits.

        Returns
        -------
        text: str
            The processed text.
        """
        return digits_re.sub("0", text)
