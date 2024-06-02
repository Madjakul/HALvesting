# halvesting/utils/data/preprocessing.py

import logging
import re
from datetime import datetime
from typing import List

from lxml.html import HtmlElement


def _parse_authors(authors: List[HtmlElement]):
    """Parses the authors into a uniform list of dict.

    Parameters
    ----------
    authors: List[lxml.html.HtmlElement]
        List of nodes of authors.

    Returns
    -------
    authors_list: List[Dict[str, str]]
        List of formated authors.
    """
    authors_list = []
    for author in authors:
        author_ = {}
        author_["affiliations"] = []
        for name in author.xpath(".//persname"):
            author_["name"] = re.sub(                                       # Joins all the words constituing the name
                r" +",
                r" ",
                "".join(name.itertext()).strip()
            )
        for e in author.xpath(".//idno | .//affiliation | .//email"):       # In the idno, affiliation or email balises
            attrib = e.attrib
            text = e.text
            if "type" in attrib:
                if attrib["type"] == "domain" or attrib["type"] == "idhal": # We don't want the mail domain nor the idhal
                    continue
                elif attrib["type"] == "md5":                               # The encrypted email adress
                    author_[attrib["type"].lower()] = text
                elif attrib["type"] == "halauthorid":                       # Then end of the halauthorid (identified author or not)
                    author_["halauthorid"] = re.sub(
                        r"(^.+)-(.+$)",
                        r"\2",
                        text
                    )
                else:
                    # We only take the unique identifier for external ids (arxiv, viaf, ...)
                    author_[attrib["type"].lower()] = re.sub(
                        r"(^.+)((?<=\/)[^\/]+$)",
                        r"\2",
                        text
                    )
            else:
                author_["affiliations"].append(
                    re.sub(r"(^.+)-(.+$)", r"\2", attrib["ref"])
                )
        authors_list.append(author_)
    return authors_list


def extract_year(date_string: str):
    """Extracts a paper's production year.

    Parameters
    ----------
    date_string : str
        Paper's production date. The format is always `%Y-%m-%d` but the precision can
        be mixed.

    Returns
    -------
    str
        Production year. If the date can't be parsed, the default year returned is '1'.
    """
    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        try:
            date_obj = datetime.strptime(date_string, "%Y-%m")
        except ValueError:
            try:
                date_obj = datetime.strptime(date_string, "%Y")
            except ValueError:
                logging.warning(f"Error parsing date: {date_string}")
                date_obj = datetime.strptime("0001", "%Y")
                year = date_obj.year
                return str(year)
    year = date_obj.year
    return str(year)


def format_hal(data: HtmlElement):
    """Parses the XML response from HAL.

    Parameters
    ----------
    data : lxml.html.HtmlElement
        Parsed XML response from HAL.

    Returns
    -------
    new_data: List[Dict[str, Any]]
        Formatted data.
    """
    new_data = []
    # For every publication returned
    for match in data.xpath("//text/listbibl/biblfull"):
        # Try to find a PDF file submitted
        pdf = match.xpath(".//editionstmt/edition/ref[contains(@subtype, 'author')]")

        # If no file submitted for this publication, pass
        if len(pdf) == 0:
            continue
        # If the submitted file is not a PDF, pass
        if not pdf[0].attrib["target"].endswith(".pdf"):
            continue
        # If the PDF is under embargo (closed access)
        if (
            datetime.strptime(pdf[0].xpath(".//date/@notbefore")[0], "%Y-%m-%d")
            > datetime.now()
        ):
            continue

        parsed_data = {}
        try:
            halid = match.xpath(".//idno[contains(@type,'halId')]")[0]
            title = match.xpath(".//title")[0]
            authors = match.xpath(".//titlestmt/author[contains(@role, 'aut')]")
            # The date is the produced year provided by HAL
            date = match.xpath(
                """.//editionstmt/edition[contains(@type, 'current')]
                /date[contains(@type, 'whenProduced')]
                """
            )[0]
            lang = match.xpath(".//profiledesc/langusage/language/@ident")[0]
            domain = match.xpath(
                """.//profiledesc/textclass
                /classcode[contains(@scheme, 'halDomain')]/@n
                """
            )
        except IndexError:
            continue
        parsed_data["halid"] = re.sub(r"(^.+)-(.+$)", r"\2", halid.text)
        parsed_data["lang"] = lang
        parsed_data["title"] = title.text
        parsed_data["domain"] = domain
        parsed_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        parsed_data["year"] = extract_year(date.text)
        # Sometimes, several PDFs are submitted by a depositor. We assume the
        # first one being the main publication.
        parsed_data["url"] = pdf[0].attrib["target"]
        parsed_data["authors"] = _parse_authors(authors)
        new_data.append(parsed_data)
    return new_data
