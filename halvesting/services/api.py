# halvesting/services/api.py

import asyncio
import logging
from typing import Optional
from urllib import parse

import aiohttp
import lxml.etree
import lxml.html

from halvesting.utils import check_dir
from halvesting.utils.data import Flusher, format_hal

_NUM_DOC_PER_FILE = 10000


class HAL:
    """Class used to interact with the `HAL's API`_ .

    Parameters
    ----------
    query : str, optional
        Search keyword.
    from_date : str, optional
        Minimum date of deposit on HAL for a given paper.
    from_hour : str, optional
        Earliest hour of deposit on HAL for a given paper on ``from_date`` day.
    to_date : str, optional
        Latest date of deposit on HAL for a given paper.
    to_hour : str, optional
        Maximum hour of deposit on HAL for a given paper on ``to_date`` day.
    response_dir : str, optional
        Path to the directory containing the JSON files with papers' metadata.

    Attributes
    ----------
    _base_url : str
        Static part of the HAL's API's URL.
    _extended_url : str
        Static part of the URL to put after ``self.query`` and before
        ``self._cursor_url``.
    _cursor_url : str
        Cursor used by the `HAL's API for pagination`_ .
    query : str, optional
        Search keyword.
    date_last_index : str, default="[* TO *]"
        This string modifies the request to restrict the upload time of the responses to
        a given time frame.
    response_dir : str, default="./data/responses"
        Path to the directory containing the JSON files with papers' metadata.


    ..  _`HAL's API`: https://api.archives-ouvertes.fr/docs`
    ..  _`HAL's API for pagination`: https://api.archives-ouvertes.fr/docs/search/?#pagination
    """

    _base_url = "https://api.archives-ouvertes.fr/search/?q="
    _extended_url = (
        "&fq=openAccess_bool:true&wt=xml-tei&sort=docid asc&rows=500&cursorMark="
    )

    def __init__(
        self,
        query: Optional[str] = None,
        from_date: Optional[str] = None,
        from_hour: Optional[str] = None,
        to_date: Optional[str] = None,
        to_hour: Optional[str] = None,
        response_dir: Optional[str] = None,
    ):
        self._cursor_url = "*"
        self.query = query if query is not None else "*"
        self.response_dir = (
            check_dir(response_dir)
            if response_dir is not None
            else check_dir("./data/response")
        )
        if from_date is not None:
            from_hour = from_hour if from_hour is not None else "00:00:00"
            self.date_last_index = (
                f"&fq=dateLastIndexed_tdate:[{from_date}T{from_hour}Z "
            )
        else:
            self.date_last_index = f"&fq=dateLastIndexed_tdate:[* "
        if to_date is not None:
            to_hour = to_hour if to_hour is not None else "00:00:00"
            self.date_last_index += f"TO {to_date}T{to_hour}Z]"
        else:
            self.date_last_index += f"TO *]"

    def __call__(self):
        """Start crawling through HAL and format the returned documents
        concurrently."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get())

    async def _scrape(self, queue: asyncio.Queue):
        """Scrape HAL API to get documents.

        Parameters
        ----------
        queue : asyncio.Queue
            Asynchronous queue for storing scraped data.
        """
        url = parse.quote(
            f"{self._base_url}{self.query}{self.date_last_index}"
            + f"{self._extended_url}{self._cursor_url}",
            safe="?/:&=*+-_[]",
        )  # base url
        logging.info(url)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.read()

            xml_data = lxml.html.fromstring(data)
            measures = xml_data.findall(".//measure")
            # Total number of match
            search_results = int(measures[0].attrib["quantity"])
            logging.info(f"Found {search_results} matchs")
            # Number of returned documents
            document_results = int(measures[1].attrib["quantity"])

            while document_results != 0:  # While the API keeps finding matches
                await queue.put(xml_data)
                self._cursor_url = xml_data.attrib["next"]
                url = parse.quote(
                    f"{self._base_url}{self.query}{self.date_last_index}"
                    + f"{self._extended_url}{self._cursor_url}",
                    safe="?/:&=*+-_[]",
                )
                logging.info(url)

                async with session.get(url) as response:
                    data = await response.read()

                xml_data = lxml.html.fromstring(data)
                measures = xml_data.findall(".//measure")
                # Number of returned documents
                document_results = int(measures[1].attrib["quantity"])

        await queue.put(None)

    async def _format(self, queue: asyncio.Queue):
        """Format the scraped data and save it.

        Parameters
        ----------
        queue : asyncio.Queue
            Asynchronous queue for storing scraped data.
        """
        with Flusher(self.response_dir, _NUM_DOC_PER_FILE) as flusher:
            while True:
                data = await queue.get()

                if data is None:
                    break

                formatted_data = format_hal(data)
                flusher.save(formatted_data)

    async def get(self):
        """Crawls through HAL and formats the returned documents
        concurrently."""
        queue = asyncio.Queue()
        # Queue like asynchronous task
        await asyncio.gather(self._scrape(queue), self._format(queue))
