# halversting/utils/data/postprocessing.py

import os
import re
import glob
import json
import hashlib
import asyncio
import tarfile
import zipfile
from typing import Dict
from collections import defaultdict

import aiofiles


_DOC_PER_JS = 1000


class Postprocessing():
    """Formats the papers in json lines format and compresses it. Papers
    written in the same language are compiled in a same json lines file, before
    before being put in a folder titled with it ISO 639 language code.

    Parameters
    ----------
    js_folder: str
        Path to the folder containing the formatted response from the HAL's
        API.
    txt_folder:
        Path to the folder containing the fulltext of each paper in a `txt`
        format.
    hf_folder: str
        Path to the folder where the postprocessed data will be written into.

    Attributes
    ----------
    js_folder: str
        Path to the folder containing the formatted response from the HAL's
        API.
    txt_folder:
        Path to the folder containing the fulltext of each paper in a `txt`
        format.
    hf_folder: str
        Path to the folder where the postprocessed data will be written into.
    lang: defaultdict(lambda: defaultdict(int))
        This dictionary stores each ISO 639 language code encountered on HAL
        and count the number of papers in a given language. Once the number of
        papers for a given language reaches ``_DOC_PER_JS``, a new json lines
        file is written to disk, compressed and stored in the correct folder.
        A second counter is then incremented to keep track of the number of
        json lines file for a given language.
    """

    def __init__(self, js_folder: str, txt_folder: str, hf_folder: str):
        self.js_folder = js_folder.rstrip("/")
        self.txt_folder = txt_folder.rstrip("/")
        self.hf_folder = hf_folder.rstrip("/")
        self.lang = defaultdict(lambda: defaultdict(int))
        self._get_last_idx()


    def __call__(self):
        asyncio.run(self.postprocess())


    async def _get_papers(self, queue: asyncio.Queue):
        js_files = os.listdir(self.js_folder)
        for js_file in js_files:
            async with aiofiles.open(
                f"{self.js_folder}/{js_file}", "r", encoding="utf-8"
            ) as jf:
                js_ = await jf.read()
                js = json.loads(js_)
            for metadata in js:
                await queue.put(metadata)
        await queue.put(None)


    async def _append_metadata(self, metadata: Dict[str, str], lang: str):
        folder = f"{self.hf_folder}/{lang}"
        if not os.path.exists(folder):
            os.makedirs(folder)
        async with aiofiles.open(
            f"{folder}/{lang}-{self.lang[lang]['counter']}.jsonl",
            "a"
        ) as jf:
            await jf.write(json.dumps(metadata, ensure_ascii=False) + "\n")


    async def _format(self, queue: asyncio.Queue):
        while True:
            metadata = await queue.get()

            if metadata is None:
                break

            iso_code = metadata["lang"]
            text = self._read_txt(metadata["halid"])

            if text is None:
                continue
                
            self.lang[iso_code]["nb_files"] += 1

            # Heuristic used to drop the corrupted txts.
            str_text = text.decode("utf-8")
            pattern = re.compile("¼|¾")
            if re.search(pattern, str_text):
                continue

            metadata["text"] = str_text
            await self._append_metadata(metadata,iso_code)

            if self.lang[iso_code]["nb_files"] == _DOC_PER_JS:
                self._compress(iso_code)
        for iso_code in self.lang.keys():
            try:
                self._compress(iso_code)
            except FileNotFoundError:
                continue


    def _get_last_idx(self):
        langs = os.listdir(self.hf_folder)
        if not langs:
            return
        for iso_code in langs:
            files = glob.glob(f"{self.hf_folder}/{iso_code}/*.tar.gz")
            latest_file = max(files, key=os.path.getctime)
            latest_index = int(re.sub(r"[^0-9]+", "", latest_file))
            self.lang[iso_code]["counter"] = latest_index + 1


    def _read_txt(self, halid: str):
        with zipfile.ZipFile(self.txt_folder, "r", zipfile.ZIP_DEFLATED) as zf:
            path = f"txts/{halid}.grobid.txt"
            if path in zf.namelist():
                with zf.open(f"txts/{halid}.grobid.txt", "r") as f:
                    text = f.read()
            else:
                return None
        return text


    def _compress(self, lang: str):
        folder = f"{self.hf_folder}/{lang}"
        path_template = f"{folder}/{lang}-{self.lang[lang]['counter']}"
        tgz_filename = f"{path_template}.tar.gz"
        jsl_filename = f"{path_template}.jsonl"
        with tarfile.open(tgz_filename, "w:gz") as tgf:
            tgf.add(jsl_filename, arcname=os.path.basename(jsl_filename))
        os.remove(jsl_filename)
        self._generate_checksum(
            lang=lang,
            folder=folder,
            tgz_filename=tgz_filename
        )
        self.lang[lang]["counter"] += 1
        self.lang[lang]["nb_files"] = 0


    def _generate_checksum(self, lang: str, folder: str, tgz_filename: str):
        checksum_filename = f"{folder}/checksum.sha256"

        hasher = hashlib.sha256()
        with open(tgz_filename, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                hasher.update(chunk)

        checksum = hasher.hexdigest()
        with open(checksum_filename, "a") as f:
            f.write(
                f"{checksum}\t{lang}-{self.lang[lang]['counter']}.tar.gz\n"
            )


    async def postprocess(self):
        """Computes a queue like asynchronous routine that get the preprocessed
        responses from HAL with their fulltext and format it in json lines
        files before compressing them.
        """
        queue = asyncio.Queue()
        await asyncio.gather(self._get_papers(queue), self._format(queue))

