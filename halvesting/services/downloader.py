# halvesting/services/downloader.py

import asyncio
import json
import logging
import os
import sys
import time

import aiofiles
import aiohttp
from tqdm import tqdm

from halvesting.utils import check_dir

_CONNECTOR = aiohttp.TCPConnector(force_close=True)


class PDF:
    """Class used to download PDF files from a list of URLs contained within a
    JSON file.

    Examples
    --------
    >>> from halvesting.services import PDF
    >>> PDF.download("./data/responses", "./data/pdfs", 100)
    """

    @classmethod
    def _get_urls(cls, response_dir: str):
        """Get PDF URLs from JSON files.

        Parameters
        ----------
        response_dir : str
            Directory containing the fetched data from HAL in JSON files.

        Yields
        ------
        Tuple[str, str]
            Tuple containing halid and PDF URL.
        """
        js_files = os.listdir(response_dir)

        js_paths = [
            os.path.join(response_dir, js_file)
            for js_file in js_files
            if js_file.endswith(".json")
        ]

        if not js_paths:
            sys.exit(
                f"""Directory at {response_dir} is empty or does not contain \
                `json` files."""
            )

        for js_path in js_paths:
            with open(js_path, "r", encoding="utf-8") as jsf:
                papers = json.load(jsf)
            for paper in papers:
                halid = paper["halid"]
                url = paper["url"]
                yield halid, url

    @classmethod
    def _chunked_http_client(cls, num_chunks: int):

        semaphore = asyncio.Semaphore(num_chunks)

        async def http_get(halid: str, url: str, client_session: aiohttp.ClientSession):
            """Asynchronous requester.

            Parameters
            ----------
            halid: str
                The halid of the PDF to be downloaded.
            url: str
                URLs used to download the PDF.
            client_session: ClientSession
                ``aiohttp`` client session used to get data.

            Returns
            -------
            halid: str
                The halid of the downloaded PDF.
            pdf_binary.content.read()
                PDF content.
            """
            nonlocal semaphore
            async with semaphore:
                try:
                    async with client_session.request("GET", url) as pdf_binary:
                        pdf = await pdf_binary.content.read()
                    return halid, pdf
                except (
                    aiohttp.ServerDisconnectedError,
                    aiohttp.ClientConnectorError,
                    asyncio.TimeoutError,
                ):
                    logging.warning(f"Couldn't access {halid} at {url}")
                    return halid, None

        return http_get

    @classmethod
    async def _download(cls, response_dir: str, pdf_dir: str, num_chunks: int):
        """Download PDFs from URLs found in response_dir's documents.

        Parameters
        ----------
        response_dir : str
            Directory containing the fetched data from HAL in JSON files.
        pdf_dir : str
            Target directory to download the PDFs.
        num_chunks : int
            Number of semaphores.
        """
        urls = cls._get_urls(response_dir)
        http_client = cls._chunked_http_client(num_chunks)

        async with aiohttp.ClientSession(connector=_CONNECTOR) as client_session:
            tasks = [http_client(halid, url, client_session) for halid, url in urls]
            for future in tqdm(asyncio.as_completed(tasks)):
                halid, pdf = await future

                if pdf is None:
                    continue

                pdf_file = os.path.join(check_dir(pdf_dir), f"{halid}.pdf")
                logging.info(pdf_file)
                async with aiofiles.open(pdf_file, "wb") as f:
                    await f.write(pdf)

    @classmethod
    def download(cls, response_dir: str, pdf_dir: str, num_chunks: int):
        """Download PDFs from URLs found in response_dir's documents.

        Parameters
        ----------
        response_dir: str
            Directory containing the fetched data from HAL in JSON files.
        pdf_dir: str
            Target directory to download the PDFs.
        num_chunks: int
            Number of semaphores.
        """
        if pdf_dir is None:
            raise TypeError("``pdf_dir`` expected ``str`` but got ``None``")
        if num_chunks is None:
            raise TypeError("``num_chunks`` expected ``int`` but got ``None``")

        loop = asyncio.get_event_loop()
        start = time.time()
        loop.run_until_complete(cls._download(response_dir, pdf_dir, num_chunks))
        end = time.time()
        logging.info(f"Time: {end - start}")
