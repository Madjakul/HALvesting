# halvesting/services/enrisher.py

from typing import Any, Dict, List, Optional, Union

from kenlm import Model
from sentencepiece import SentencePieceProcessor
from transformers import AutoModel

from halvesting.utils.data import Postprocessing


def enrich(
    documents: Dict[str, List[Any]],
    sentencepiece_model: Union[SentencePieceProcessor, None],
    kenlm_model: Union[Model, None],
    lang: str,
    tokenizer: Optional[AutoModel] = None,
):
    """Computes some statistics on a batch of documents. The documents need to
    follow the HALvesting's `json` format.

    Parameters
    ----------
    documents: Dict[str, List[Any]]
        Batch of documents already formatted by HALvesting.
    sentencepiece_model: Union[sentencepiece.SentencePieceProcessor, None]
        The tokenizer used to encode text for the `kenlm_model`.
    kenlm_model: kenlm.Model
        Language model used to compute the perplexity.
    lang: str
        ISO-639 language code of the batch of documents.
    tokenizer: transformers.AutoModel, optional
        Custom HuggingFace tokenizer's checkpoint. Can also be the path to
        a local checkpoint.

    Returns
    -------
    documents: Dict[str, List[Any]]
        The enrished batch of documents.
    """
    texts = []
    token_count = []
    rps_doc_frac_all_caps_words = []
    rps_doc_frac_lines_end_with_ellipsis = []
    rps_doc_frac_no_alph_words = []
    rps_doc_lorem_ipsum = []
    rps_doc_mean_word_length = []
    rps_doc_stop_word_fraction = []
    rps_doc_symbol_to_word_ratio = []
    rps_doc_frac_unique_words = []
    rps_doc_unigram_entropy = []
    rps_doc_word_count = []
    doc_frac_lines_ending_with_terminal_punctution_mark = []
    rps_lines_frac_start_with_bulletpoint = []
    rps_doc_num_sentences = []
    rps_frac_chars_in_dupe_5grams = []
    rps_frac_chars_in_dupe_6grams = []
    rps_frac_chars_in_dupe_7grams = []
    rps_frac_chars_in_dupe_8grams = []
    rps_frac_chars_in_dupe_9grams = []
    rps_frac_chars_in_dupe_10grams = []
    kenlm_pp = []

    for text in documents["text"]:
        document = Postprocessing(text=text, lang=lang, tokenizer=tokenizer)
        texts.append(document.raw_content)
        token_count.append(document.count_tokens())
        rps_doc_frac_all_caps_words.append(document.rps_doc_frac_all_caps_words())
        rps_doc_frac_lines_end_with_ellipsis.append(
            document.rps_doc_frac_lines_end_with_ellipsis()
        )
        rps_doc_frac_no_alph_words.append(document.rps_doc_frac_no_alph_words())
        rps_doc_lorem_ipsum.append(document.rps_doc_lorem_ipsum())
        rps_doc_mean_word_length.append(document.rps_doc_mean_word_length())
        rps_doc_stop_word_fraction.append(document.rps_doc_stop_word_fraction())
        rps_doc_symbol_to_word_ratio.append(document.rps_doc_symbol_to_word_ratio())
        rps_doc_frac_unique_words.append(document.rps_doc_frac_unique_words())
        rps_doc_unigram_entropy.append(document.rps_doc_unigram_entropy())
        rps_doc_word_count.append(document.rps_doc_word_count())
        doc_frac_lines_ending_with_terminal_punctution_mark.append(
            document.doc_frac_lines_ending_with_terminal_punctution_mark()
        )
        rps_lines_frac_start_with_bulletpoint.append(
            document.rps_lines_frac_start_with_bulletpoint()
        )
        rps_doc_num_sentences.append(document.rps_doc_num_sentences())
        rps_frac_chars_in_dupe_5grams.append(document.rps_frac_chars_in_dupe_ngrams(5))
        rps_frac_chars_in_dupe_6grams.append(document.rps_frac_chars_in_dupe_ngrams(6))
        rps_frac_chars_in_dupe_7grams.append(document.rps_frac_chars_in_dupe_ngrams(7))
        rps_frac_chars_in_dupe_8grams.append(document.rps_frac_chars_in_dupe_ngrams(8))
        rps_frac_chars_in_dupe_9grams.append(document.rps_frac_chars_in_dupe_ngrams(9))
        rps_frac_chars_in_dupe_10grams.append(
            document.rps_frac_chars_in_dupe_ngrams(10)
        )
        if (sentencepiece_model or kenlm_model) is None:
            kenlm_pp.append(None)
        else:
            kenlm_pp.append(
                document.compute_perplexity(sentencepiece_model, kenlm_model)  # type: ignore
            )

    documents["text"] = texts
    documents["token_count"] = token_count
    documents["rps_doc_frac_all_caps_words"] = rps_doc_frac_all_caps_words
    documents["rps_doc_frac_lines_end_with_ellipsis"] = (
        rps_doc_frac_lines_end_with_ellipsis
    )
    documents["rps_doc_frac_no_alph_words"] = rps_doc_frac_no_alph_words
    documents["rps_doc_lorem_ipsum"] = rps_doc_lorem_ipsum
    documents["rps_doc_mean_word_length"] = rps_doc_mean_word_length
    documents["rps_doc_stop_word_fraction"] = rps_doc_stop_word_fraction
    documents["rps_doc_symbol_to_word_ratio"] = rps_doc_symbol_to_word_ratio
    documents["rps_doc_frac_unique_words"] = rps_doc_frac_unique_words
    documents["rps_doc_unigram_entropy"] = rps_doc_unigram_entropy
    documents["rps_doc_word_count"] = rps_doc_word_count
    documents["doc_frac_lines_ending_with_terminal_punctution_mark"] = (
        doc_frac_lines_ending_with_terminal_punctution_mark
    )
    documents["rps_lines_frac_start_with_bulletpoint"] = (
        rps_lines_frac_start_with_bulletpoint
    )
    documents["rps_doc_num_sentences"] = rps_doc_num_sentences
    documents["rps_frac_chars_in_dupe_5grams"] = rps_frac_chars_in_dupe_5grams
    documents["rps_frac_chars_in_dupe_6grams"] = rps_frac_chars_in_dupe_6grams
    documents["rps_frac_chars_in_dupe_7grams"] = rps_frac_chars_in_dupe_7grams
    documents["rps_frac_chars_in_dupe_8grams"] = rps_frac_chars_in_dupe_8grams
    documents["rps_frac_chars_in_dupe_9grams"] = rps_frac_chars_in_dupe_9grams
    documents["rps_frac_chars_in_dupe_10grams"] = rps_frac_chars_in_dupe_10grams
    documents["kenlm_pp"] = kenlm_pp

    return documents
