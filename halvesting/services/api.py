# halvesting/services/api.py

import logging
import asyncio
from urllib import parse
from typing import Optional
from datetime import datetime

import aiohttp
import lxml.html
import lxml.etree

from halvesting.utils.data import Flusher, format_hal
from halvesting.utils import check_dir


_DOC_PER_JS = 10000


class HAL():
    """Class used to interact with the
    `HAL's API https://api.archives-ouvertes.fr/docs`__.

    Parameters
    ----------
    query: str, optional
        Search keyword.
    from_date: str, optional
        Minimum date of deposit on HAL for a given paper.
    from_hour: str, optional
        Earliest hour of deposit on HAL for a given paper on ``from_date`` day.
    to_date: str, optional
        Latest date of deposit on HAL for a given paper.
    to_hour: str, optional
        Maximum hour of deposit on HAL for a given paper on ``to_date`` day.
    response_dir: str, optional
        Path to the directory containing the `json` files with papers'
        metadata.

    Attributes
    ----------
    _base_url: str
        Static part of the HAL's API's URL.
    _extended_url: str
        Static part of the URL to put after ``self.query`` and before
        ``self._cursor_url``.
    _cursor_url: str
        Cursor used by the HAL's API for pagination:
        `https://api.archives-ouvertes.fr/docs/search/?#pagination`__
    query: str, optional
        Search keyword.
    date_last_index: str, default="[* TO *]"
        This string modifies the request to
        "[``from_date``T``from_hour``Z TO ``to_date``T``to_hour``Z]" in order
        to restrict the responses to a given time frame.
    response_dir: str, default="./data/responses"
        Path to the directory containing the `json` files with papers'
        metadata.
    """

    _base_url = "https://api.archives-ouvertes.fr/search/?q="
    _extended_url = "&fq=openAccess_bool:true&wt=xml-tei&sort=docid asc&rows=500&cursorMark="

    def __init__(
        self, query: Optional[str]=None, from_date: Optional[str]=None,
        from_hour: Optional[str]=None, to_date: Optional[datetime]=None,
        to_hour: Optional[str]=None, response_dir: Optional[str]=None
    ):
        self._cursor_url = "*"
        self.query = query if query is not None else "*"
        self.response_dir = check_dir(response_dir) \
            if response_dir is not None else check_dir("./data/response")
        if from_date is not None:
            from_hour = from_hour if from_hour is not None else "00:00:00"
            self.date_last_index = \
                f"&fq=dateLastIndexed_tdate:[{from_date}T{from_hour}Z "
        else:
            self.date_last_index = \
                f"&fq=dateLastIndexed_tdate:[* "
        if to_date is not None:
            to_hour = to_hour if to_hour is not None else "00:00:00"
            self.date_last_index += f"TO {to_date}T{to_hour}Z]"
        else:
            self.date_last_index += f"TO *]"


    def __call__(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get())


    async def _scrape(self, queue: asyncio.Queue):
        url = parse.quote(
            f"{self._base_url}{self.query}{self.date_last_index}"
            + f"{self._extended_url}{self._cursor_url}",
            safe="?/:&=*+-_[]"
        )                                                               # base url
        logging.info(url)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.read()

            xml_data = lxml.html.fromstring(data)
            measures = xml_data.findall(".//measure")
            search_results = int(measures[0].attrib["quantity"])        # Total number of match
            logging.info(f"Found {search_results} matchs")
            document_results = int(measures[1].attrib["quantity"])      # Number of returned documents

            while document_results != 0:                                # While the API keeps finding matches
                await queue.put(xml_data)
                self._cursor_url = xml_data.attrib["next"]
                url = parse.quote(
                    f"{self._base_url}{self.query}{self.date_last_index}"
                    + f"{self._extended_url}{self._cursor_url}",
                    safe="?/:&=*+-_[]"
                )
                logging.info(url)

                async with session.get(url) as response:
                    data = await response.read()

                xml_data = lxml.html.fromstring(data)
                measures = xml_data.findall(".//measure")
                document_results = int(measures[1].attrib["quantity"])  # Number of returned documents

        await queue.put(None)


    async def _format(self, queue: asyncio.Queue):
        with Flusher(self.response_dir, _DOC_PER_JS) as flusher:
            while True:
                data = await queue.get()

                if data is None:
                    break

                formated_data = format_hal(data)
                flusher.save(formated_data)


    async def get(self):
        """Crawls through HAL and formats the returned documents concurantly.
        """
        queue = asyncio.Queue()
        await asyncio.gather(self._scrape(queue), self._format(queue))  # Queue like asynchronous task

