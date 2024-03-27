# halvesting/services/enrisher.py

import re

import ftfy

from halvesting.utils.data import (DIGITS_RE, NON_PRINTING_CHAR_RE,
                                   UNICODE_PUNCTUATION, Postprocessing)


def remove_non_printing_characters(document, non_printing_characters_re):
    return non_printing_characters_re.sub("", document)


def remove_extra_newlines(text: str):
    text = re.sub(r"\n\n+", "\n\n", text)
    text = re.sub(r"^\n+", "", text)
    text = re.sub(r"\n+$", "", text)
    return text


def uniform_whitespace(
    document,
    whitespace=[
        " ",
        " ",
        " ",
        " ",
        " ",
        "　",
        " ",
        " ",
        " ",
        " ",
        "￼",
        "",
    ],
):
    """There are different whitespace characters."""
    whitespace = set(whitespace)
    document = "".join([char if char not in whitespace else " " for char in document])
    return document


def replace_digits_with_zeros(document, digits_re):
    return digits_re.sub("0", document)


def replace_unicode_punctuation(document, unicode_punctuation):
    return "".join(unicode_punctuation.get(c, c) for c in document)


def normalization(
    document,
    do_remove_non_printing_characters,
    strip,
    lower_case,
    do_uniform_whitespace,
    do_replace_digits_with_zeros,
    do_replace_unicode_punctuation,
    non_printing_characters_re=NON_PRINTING_CHAR_RE,
    digits_re=DIGITS_RE,
    unicode_punctuation=UNICODE_PUNCTUATION,
):
    if do_remove_non_printing_characters:
        document = remove_non_printing_characters(document, non_printing_characters_re)
    if strip:
        document = document.strip()
    if not document:
        return document
    if lower_case:
        document = document.lower()
    if do_uniform_whitespace:
        document = uniform_whitespace(document)
    if do_replace_digits_with_zeros:
        document = replace_digits_with_zeros(document, digits_re)
    if do_replace_unicode_punctuation:
        document = replace_unicode_punctuation(document, unicode_punctuation)
    return document


def tokenization(document, sentencepiece_model, join_on_whitespace):
    document_tokenized = sentencepiece_model.encode_as_pieces(document)
    if join_on_whitespace:
        document_tokenized = " ".join(document_tokenized)
    return document_tokenized


def detect_lang(text, langid_model):
    language, score = langid_model.predict(text.replace("\n", ""))
    language = language[0].split("__")[2]
    return {"lang": language, "score": score[0]}


def compute_perplexity_score(
    document, sentencepiece_models, kenlm_models, langid_model
):
    document = normalization(
        document=document,
        do_remove_non_printing_characters=True,
        strip=True,
        lower_case=False,
        do_uniform_whitespace=True,
        do_replace_digits_with_zeros=True,
        do_replace_unicode_punctuation=True,
    )

    doc_log_score, doc_length = 0, 0
    for line in document.split("\n"):
        lang = detect_lang(line, langid_model)["lang"]
        if lang not in sentencepiece_models:
            # doc_length += len(line.split()) + 1
            doc_length += 0.00000000001
            doc_log_score += 0.00000000001
            continue
        line = tokenization(line, sentencepiece_models[lang], join_on_whitespace=True)
        log_score = kenlm_models[lang].score(line)
        length = len(line.split()) + 1
        doc_log_score += log_score
        doc_length += length
    pp_score = 10.0 ** (-doc_log_score / doc_length)
    pp_score = round(pp_score, 1)
    return pp_score


def enrish(
    document,
    sentencepiece_models,
    kenlm_models,
    tokenizer,
    word_tokenizer,
    langid_model,
):
    document["text"] = (
        ftfy.fix_text(document["text"]).replace("\u202b", "").replace("\u202c", "")
    )
    document["text"] = remove_extra_newlines(document["text"])
    document["kenlm_pp"] = compute_perplexity_score(
        document["text"], sentencepiece_models, kenlm_models, langid_model
    )

    _document = Postprocessing(
        document["text"], tokenizer=tokenizer, word_tokenizer=word_tokenizer
    )

    document["rps_doc_word_count"] = _document.rps_doc_word_count()
    document["token_count"] = _document.count_tokens(document["text"])
    document["rps_doc_frac_all_caps_words"] = _document.rps_doc_frac_all_caps_words()
    document["rps_doc_frac_no_alph_words"] = _document.rps_doc_frac_no_alph_words()
    document["rps_doc_lorem_ipsum"] = _document.rps_doc_lorem_ipsum()
    document["rps_doc_mean_word_length"] = _document.rps_doc_mean_word_length()
    document["rps_doc_symbol_to_word_ratio"] = _document.rps_doc_symbol_to_word_ratio()
    document["rps_doc_frac_unique_words"] = _document.rps_doc_frac_unique_words()

    return document
