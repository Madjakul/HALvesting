# halvesting/services/filtering.py

from typing import Any, Dict, List


def _compute_sterility(word_count: int, token_count: int):
    """Computes the ratio of number of words divided by the number of tokens.

    Parameters:
    -----------
    word_count: int
        Number of words.
    token_count: int
        Number of tokens.

    Returns
    -------
    sterility: float
        Word count divided by token count.
    """
    sterility = word_count / token_count
    return round(sterility, 3)


def filter_(batch: Dict[str, List[Any]]):
    """Filter a batch of texts based on various criteria.

    Parameters
    ----------
    batch : Dict[str, List[Any]]
        A dictionary containing lists of various features related to the texts.

    Returns
    -------
    mask : List[bool]
        A list of boolean values indicating whether each text passes the filtering
        criteria.
    """
    mask = []
    for i in range(len(batch["halid"])):
        # If the text is empty or near empty
        if len(batch["text"][i].split()) < 3:
            mask.append(False)
            continue

        # If there are too many uppercased words
        if batch["rps_doc_frac_all_caps_words"][i] > 0.1:
            mask.append(False)
            continue

        # If the text has more than 60% of no alphanumerical words
        if batch["rps_doc_frac_no_alph_words"][i] > 0.6:
            mask.append(False)
            continue

        # If the text has too much "lorem ipsum" text
        if batch["rps_doc_lorem_ipsum"][i] > 0.2:
            mask.append(False)
            continue

        # If words are shorter than 1.5 words on average
        if batch["rps_doc_mean_word_length"][i] < 1.5:
            mask.append(False)
            continue

        # If there are no stop words in the text
        if batch["rps_doc_stop_word_fraction"][i] == 0:
            mask.append(False)
            continue

        # If the text is overtoknized
        if (
            _compute_sterility(batch["rps_doc_word_count"][i], batch["token_count"][i])
            < 0.2
        ):
            mask.append(False)
            continue

        mask.append(True)
    return mask
