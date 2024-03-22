# halvesting/utils/data/flusher.py

import json
import os
from datetime import datetime
from typing import Any, Dict, List


class Flusher:
    """Writes batch of data in a given `json` file in an asynchronous way.

    Parameters
    ----------
    batch_size: int
        Maximum batch size to keep in the buffer before writing to disk.
    name: str
        File to write into.

    Attributes
    ----------
    batch_size: int
        Maximum batch size to keep in the buffer before writing to disk.
    name: str
        File to write into.
    batch: List[Dict[str, Any]]
        List containing each data point.
    """

    def __init__(self, dir: str, batch_size: int):
        self.batch_size = batch_size
        self.dir = dir
        self.counter = 1
        self.batch = []

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.flush()

    def save(self, data_point: List[Dict[str, Any]]):
        """Saves several data_points in the buffer. When the nnumber of data
        points reaches ``self.batch_size``, the batch is written to disk.

        Parameters
        ----------
        data_point: List[Dict[str, Any]]
            Data point.
        """
        # self.batch.append(data_point)
        self.batch.extend(data_point)
        if len(self.batch) >= self.batch_size:
            self.flush()

    def flush(self):
        """Writes the data in ``self.batch`` to disk."""
        now = datetime.now()
        now_s = now.strftime("%Y-%m-%d")
        js_file = os.path.join(self.dir, f"{now_s}_{self.counter}.json")
        with open(js_file, "w") as f:
            json.dump(self.batch, f, ensure_ascii=False, indent=4)
            f.flush()
        self.batch.clear()
        self.counter += 1
