# halvesting/services/merger.py

import asyncio
import glob
import json
import os
import re
import zipfile
from collections import defaultdict
from typing import Dict

import aiofiles

import halvesting.utils.utils as utils

_NUM_DOC_PER_FILE = 2000


class Merger:
    """Formats the papers in JSON lines format and compresses it. Papers
    written in the same language are compiled in a same JSON lines file, before
    being put in a folder titled with its ISO 639 language code.

    Parameters
    ----------
    js_dir_path: str
        Path to the folder containing the formatted response from the HAL's API.
    txts_dir_path: str
        Path to the folder containing the fulltext of each paper in a TXT format.
    output_dir_path: str
        Path to the folder where the postprocessed data will be written into.
    version: str
        Version of the dump starting by "1.0".

    Attributes
    ----------
    js_dir_path: str
        Path to the folder containing the formatted response from the HAL's API.
    txts_dir_path: str
        Path to the folder containing the fulltext of each paper in a `txt` format.
    output_dir_path: str
        Path to the folder where the postprocessed data will be written into.
    version: str
        Version of the dump starting by "1.0".
    lang: defaultdict(lambda: defaultdict(int))
        This dictionary stores each ISO 639 language code encountered on HAL and counts
        the number of papers in a given language. Once the number of papers for a given
        language reaches ``_DOC_PER_JS``, a new JSON lines file is written to disk,
        compressed, and stored in the correct folder. A second counter is then
        incremented to keep track of the number of JSON lines files for a given
        language.
    """

    def __init__(
        self, js_dir_path: str, txts_dir_path: str, output_dir_path: str, version: str
    ):
        self.js_dir_path = js_dir_path
        self.txts_dir_path = txts_dir_path
        self.output_dir_path = output_dir_path
        self.version = version
        self.lang = defaultdict(lambda: defaultdict(int))

    def __call__(self):
        asyncio.run(self.postprocess())

    async def _get_papers(self, queue: asyncio.Queue):
        """Retrieves papers' metadata from JSON files asynchronously.

        Parameters
        ----------
        queue : asyncio.Queue
            Asynchronous queue to store papers' metadata.
        """
        js_file_paths = os.listdir(self.js_dir_path)
        for js_file_path in js_file_paths:
            js_file_path = os.path.join(self.js_dir_path, js_file_path)
            async with aiofiles.open(js_file_path, "r", encoding="utf-8") as f:
                jsf = await f.read()
                js = json.loads(jsf)
            for metadata in js:
                await queue.put(metadata)
        await queue.put(None)

    async def _append_metadata(self, metadata: Dict[str, str], lang: str):
        """Appends metadata to JSON lines file.

        Parameters
        ----------
        metadata : Dict[str, str]
            Metadata of the paper.
        lang : str
            ISO 639 language code.
        """
        lang_dir_path = utils.check_dir(os.path.join(self.output_dir_path, lang))
        output_file_path = os.path.join(
            lang_dir_path, f"{lang}{self.version}-{self.lang[lang]['counter']}.jsonl"
        )
        async with aiofiles.open(output_file_path, "a") as f:
            await f.write(json.dumps(metadata, ensure_ascii=False) + "\n")

    async def _format(self, queue: asyncio.Queue):
        """Formats papers' metadata and full text asynchronously.

        Parameters
        ----------
        queue : asyncio.Queue
            Asynchronous queue containing papers' metadata.
        """
        while True:
            metadata = await queue.get()

            if metadata is None:
                break

            iso_code = metadata["lang"]
            text = self._read_txt(metadata["halid"])

            if not text:
                continue

            self.lang[iso_code]["nb_files"] += 1

            str_text = text.decode("utf-8")

            # Empty files
            if not str_text:
                continue
            pattern = re.compile(r"^[\s\n]*$")
            if re.search(pattern, str_text):
                continue

            metadata["text"] = str_text
            await self._append_metadata(metadata, iso_code)

            if self.lang[iso_code]["nb_files"] == _NUM_DOC_PER_FILE:
                utils.compress(
                    lang=iso_code,
                    hf_dir_path=self.output_dir_path,
                    counter=self.lang[iso_code]["counter"],
                    version=self.version,
                )
                self.lang[iso_code]["counter"] += 1
                self.lang[iso_code]["nb_files"] = 0
        for iso_code in self.lang.keys():
            try:
                utils.compress(
                    lang=iso_code,
                    hf_dir_path=self.output_dir_path,
                    counter=self.lang[iso_code]["counter"],
                    version=self.version,
                )
                self.lang[iso_code]["counter"] += 1
                self.lang[iso_code]["nb_files"] = 0
            except FileNotFoundError:
                continue

    def _read_txt(self, halid: str):
        """Reads full text from the TXT file.

        Parameters
        ----------
        halid : str
            HAL ID of the paper.

        Returns
        -------
        bytes
            Full text of the paper in bytes format.
        """
        with zipfile.ZipFile(self.txts_dir_path, "r", zipfile.ZIP_DEFLATED) as zf:
            path = f"txts/{halid}.grobid.txt"
            if path in zf.namelist():
                with zf.open(f"txts/{halid}.grobid.txt", "r") as f:
                    text = f.read()
            else:
                return None
        return text

    async def postprocess(self):
        """Asynchronously computes the post-processing routine that gets the
        preprocessed responses from HAL with their fulltext and formats it in
        JSON lines files before compressing them."""
        queue = asyncio.Queue()
        await asyncio.gather(self._get_papers(queue), self._format(queue))
