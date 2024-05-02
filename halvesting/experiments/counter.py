# halvesting/experiments/counter.py

import logging
from collections import defaultdict
from typing import Any, Dict, List

from datasets import DatasetDict
from tqdm import tqdm
from transformers import AutoTokenizer

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
_TOKENIZER = AutoTokenizer.from_pretrained("google/mt5-base", use_fast=False)


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


def _count_all_tokens(documents: Dict[str, List[Any]]):
    """Count the tokens in each document.

    Parameters
    ----------
    documents : dict
        Dictionary containing lists of text documents.

    Returns
    -------
    dict
        Dictionary containing lists of text documents with an additional 'token_count'
        list.
    """
    token_count = []
    for text in documents["text"]:
        token_count.append(len(_TOKENIZER.encode(text, add_special_tokens=False)))
    documents["token_count"] = token_count
    return documents


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


def count_doc_and_tokens(dataset: DatasetDict, batch_size: int, num_proc: int):
    """Count the number of documents and tokens for each domain in the dataset.

    Parameters
    ----------
    dataset : DatasetDict
        Dataset containing documents.
    batch_size : int
        Batch size for processing.
    num_proc : int
        Number of processes for parallel processing.

    Returns
    -------
    defaultdict
        Dictionary containing statistics for each domain.
    """
    dataset = dataset.map(
        lambda document: _count_all_tokens(document),
        batched=True,
        batch_size=batch_size,
        num_proc=num_proc,
    )
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
