# halvesting/experiments/raw_counter.py

import logging
from collections import defaultdict

from datasets import DatasetDict
from tqdm import tqdm

_DOMAINS = (
    "shs",
    "sdv",
    "phys",
    "info",
    "spi",
    "sde",
    "chim",
    "sdu",
    "math",
    "scco",
    "stat",
    "qfin",
    "nlin",
)


def _count_documents(filtered_dataset: DatasetDict, stats: defaultdict, _domain: str):
    """Count the number of documents for a specific domain.

    Parameters
    ----------
    filtered_dataset : DatasetDict
        Filtered dataset containing documents.
    stats : defaultdict
        Dictionary to store statistics.
    _domain : str
        Domain identifier.
    """
    doc_count = len(filtered_dataset)
    logging.info(f"Found {doc_count} documents for {_domain}.")
    stats[_domain]["documents"] = doc_count


def _count_tokens(filtered_dataset: DatasetDict, stats: defaultdict, _domain: str):
    """Count the total number of tokens for a specific domain.

    Parameters
    ----------
    filtered_dataset : DatasetDict
        Filtered dataset containing documents.
    stats : defaultdict
        Dictionary to store statistics.
    _domain : str
        Domain identifier.
    """
    token_count = sum(filter(None, filtered_dataset["token_count"]))  # type: ignore
    logging.info(f"Found {token_count} tokens for {_domain}.")
    stats[_domain]["tokens"] = token_count


def count_raw_doc_and_tokens(dataset: DatasetDict) -> defaultdict:
    """Count the number of documents and tokens for each domain in the dataset.

    Parameters
    ----------
    dataset : DatasetDict
        Dataset containing documents.

    Returns
    -------
    defaultdict
        Dictionary containing statistics for each domain.
    """
    logging.info("Counting documents and tokens...")
    stats = defaultdict(lambda: defaultdict(int))
    stats["total"]["documents"] = len(dataset)
    stats["total"]["tokens"] = sum(filter(None, dataset["token_count"]))  # type: ignore
    for _domain in tqdm(_DOMAINS):
        filtered_dataset = dataset.filter(
            lambda document: any(
                [domain.startswith(_domain) for domain in document["domain"]]
            )
        )
        _count_documents(
            filtered_dataset=filtered_dataset, stats=stats, _domain=_domain
        )
        _count_tokens(filtered_dataset=filtered_dataset, stats=stats, _domain=_domain)
    return stats
