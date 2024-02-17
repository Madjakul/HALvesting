# halversting/utils/data/preprocessing.py

import re
import logging
from datetime import datetime

from lxml.html import HtmlElement


def extract_year(date_string: str):
    """Extracts a paper's production year.

    Parameters
    ----------
    date_string: str
        Paper's production's date. The format is always `%Y-%m-%d` but the
        precision can be mixed.

    Returns
    -------
    year: str
        Production's year. If the date can't be parsed, the default year
        returned is '1'.
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
                return datetime.strptime("1", "%Y")
    year = date_obj.year
    return str(year)


def format_hal(data: HtmlElement):
    """Parses the ``xml`` response from HAL.

    Parameters
    ----------
    data: lxml.html.HtmlElement
        Parsed xml response from HAL.

    Returns
    -------
    new_data: List[Dict[str, str]]
        Formatted data.
    """
    new_data = []
    # For every publication returned
    for match in data.xpath("//text/listbibl/biblfull"):
        # Try to find a PDF file submitted
        pdf = match.xpath(
            ".//editionstmt/edition/ref[contains(@subtype, 'author')]"
        )

        # If no file submitted for this publication, pass
        if len(pdf) == 0:
            continue
        # If the submitted file is not a PDF, pass
        if not pdf[0].attrib["target"].endswith(".pdf"):
            continue
        # If the PDF is under embargo (closed access)
        if (
            datetime.strptime(
                pdf[0].xpath(".//date/@notbefore")[0], "%Y-%m-%d"
            ) > datetime.now()
        ):
            continue

        parsed_data = {}
        halid = match.xpath(".//idno[contains(@type,'halId')]")[0]
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
        )[0]

        parsed_data["halid"] = re.sub(r"(^.+)-(.+$)", r"\2", halid.text)
        parsed_data["lang"] = lang
        parsed_data["domain"] = re.sub(r"(^.+)\.(.+$)", r"\1", domain)
        parsed_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        parsed_data["year"] = extract_year(date.text)
        # Sometimes, several PDFs are submitted by a depositor. We assume the
        # first one being the main publication.
        parsed_data["url"] = pdf[0].attrib["target"]
        new_data.append(parsed_data)
    return new_data

