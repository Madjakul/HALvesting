# HALvesting

Harvests open scientific papers from HAL and parses it.

---


HALvesting is a Python project designed for harvesting data from the [HAL (Hyper Articles en Ligne) repository](https://hal.science/). It provides functionalities to fetch data from HAL using specified criteria and process the fetched data for further analysis.

The latest dump can be found on [HuggingFace](huggingface.co). The update is done yearly.


## Features

- [**fetch_data.py**](fetch_data.py): This script fetches data from HAL using specified criteria such as query, date range, and output format (PDF).
- [**postprocess_data.py**](postprocess_data.py): This script is used for post-processing the fetched data.


## Requirements

In order to take full advantage of HALvesting and get the research paper's fulltexts, you'll need to install and use the following repos:

```
GROBID: A machine learning software for extracting information from scholarly documents
https://github.com/kermitt2/grobid

harvesting: Collection of data parser for harvested data in [...]
[...]
```

## Installation

1. Clone the repository
```sh
git clone https://github.com/Madjakul/HALvesting.git
```

2. Navigate to the project directory
```sh
cd HALvesting
```
3. Install the required dependencies:
```sh
pip install -r requirements.txt
```


## Usage

### Fetching Data

It is easier to modify the [`fetch_data.sh`](scripts/fetch_data.sh) directly and run it with
```sh
./scripts/fetch_data.sh
```

However, you can run the [`fetch_data.py`](fetch_data.py) script with appropriate arguments.
```
usage: fetch_data.py [--query QUERY] [--from_date %Y/%m/%d] [--from_hour %H:%M:%S] [--to_date %Y/%m/%d] [to_hour %H:%M:%S] [--pdf]

Fetch data from HAL. Can also download PDFs locally.

optional arguments:
    --query QUERY
        Search request.
    --from_date %Y/%m/%d
        Minimum deposit date on HAL.
    --from_hour %H:%M:%S
        Minimum deposit hour on a given day on HAL.
    --to_date %Y/%m/%d
        Maximum deposit date on HAL.
    --to_hour %H:%M:%S
        Maximum deposit hour on a given day on HAL.
    --pdf
        If you want to download PDFs or not. 
```

### Post-process Data

After fetching data, you can perform post-processing using the `postprocess_data.py` script.

It is easier to modify the [`postprocess_data.sh`](scripts/postprocess_data.sh) directly and run it with
```sh
./scripts/postprocess_data.sh
```

However, you can run the [`postprocess_data.py`](postprocess_data.py) script with appropriate arguments.
```
usage: postprocess_data.py --js_folder JS_FOLDER --txt_folder TXT_FOLDER --hf_folder HF_FOLDER

Format the fetched data in order to push them to HuggingFace.

arguments:
    --js_folder JS_FOLDER
        Folder containing the previously fetched data.
    --txt_folder TXT_FOLDER
        Folder containing the fulltexts of the fetched papers.
    --hf_folder HF_FOLDER
        HuggingFace folder that will be pushed to hub.
```


## Citation

If you find our work helpful, please cite the following:
```bib
@misc{HALvesting,
    title = {HALvesting},
    howpublished = {\url{https://github.com/Madjakul/HALvesting}},
    publisher = {GitHub},
    year = {2024},
    archivePrefix = {swh}
}

@proceedings{TBD
}
```


## License

This project is licensed under the [Apache License 2.0](LICENSE).
