# halversting/utils/api/hal.py

import logging
import asyncio
from urllib import parse
from datetime import datetime
from typing import Optional, Dict

import aiohttp
import aiofiles
import lxml.html
import lxml.etree

from halversting.utils.data import Flusher, format_hal


_DOC_PER_JS = 1000


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
        Minimum hour of deposit on HAL for a given paper on ``from_date`` day.
    to_date: str, optional
        Mximum date of deposit on HAL for a given paper.
    to_hour: str, optional
        Maximum hour of deposit on HAL for a given paper on ``to_date`` day.
    pdf: bool, optional
        ``True`` if you want to download the PDFs locally while fetching the
        metadatas from HAL.


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
    pdf: bool, optional
        ``True`` if you want to download the PDFs locally while fetching the
        metadatas from HAL.
    """

    _base_url = "https://api.archives-ouvertes.fr/search/?q="
    _extended_url = "&fq=openAccess_bool:true&wt=xml-tei&sort=docid asc&rows=100&cursorMark="

    def __init__(
        self, query: Optional[str]=None, from_date: Optional[str]=None,
        from_hour: Optional[str]=None, to_date: Optional[datetime]=None,
        to_hour: Optional[str]=None, pdf: Optional[bool]=None
    ):
        self._cursor_url = "*"
        self.query = query if query is not None else "*"
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
        self.pdf = pdf if pdf is not None else False


    def __call__(
        self, query: Optional[str]=None, from_date: Optional[str]=None,
        from_hour: Optional[str]=None, to_date: Optional[datetime]=None,
        to_hour: Optional[str]=None, pdf: Optional[bool]=None
    ):
        asyncio.run(self.get(query, from_date, from_hour, to_date, to_hour, pdf))


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
            logging.warning(f"Found {search_results} matchs")
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


    async def _download_pdf(
        self, name: str, url: str, session: aiohttp.ClientSession
    ):
        async with session.get(url) as response:
            async with aiofiles.open(
                f"./data/pdfs/{name}.pdf", "wb"
            ) as f:
                await f.write(await response.read())


    async def _download_pdfs(self, names_urls: Dict[str, str]):
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[
                    self._download_pdf(name, url, session) \
                    for name, url in names_urls.items()
                ]
            )


    async def _format(self, queue: asyncio.Queue):
        with Flusher("./data/responses/hal", _DOC_PER_JS) as flusher:
            while True:
                data = await queue.get()

                if data is None:
                    break

                formated_data = format_hal(data)
                flusher.save(formated_data)

                if self.pdf:
                    names_urls = {
                        data_point["halid"]: data_point["url"] \
                        for data_point in formated_data
                    }
                    await self._download_pdfs(names_urls)


    async def get(
        self, query: Optional[str]=None, from_date: Optional[str]=None,
        from_hour: Optional[str]=None, to_date: Optional[datetime]=None,
        to_hour: Optional[str]=None, pdf: Optional[bool]=None
    ):
        """Crawls through HAL and formats the returned documents concurantly.

        Parameters
        ----------
        query: str, optional
            Search keyword.
        from_date: str, optional
            Minimum date of deposit on HAL for a given paper.
        from_hour: str, optional
            Minimum hour of deposit on HAL for a given paper on ``from_date``
            day.
        to_date: str, optional
            Mximum date of deposit on HAL for a given paper.
        to_hour: str, optional
            Maximum hour of deposit on HAL for a given paper on ``to_date``
            day.
        pdf: bool, optional
            ``True`` if you want to download the PDFs locally while fetching
            the metadatas from HAL.
        """
        if query is not None:
            self.query = query
        if pdf is not None:
            self.pdf = pdf
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
        queue = asyncio.Queue()
        await asyncio.gather(self._scrape(queue), self._format(queue))  # Queue like asynchronous task

