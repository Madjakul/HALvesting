# HALvesting

[![arXiv](https://img.shields.io/badge/arXiv-2407.20595-b31b1b.svg)](https://arxiv.org/abs/2407.20595)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-Data-yellow)](https://huggingface.co/datasets/almanach/HALvest)

Harvests open scientific papers from HAL.

---


HALvesting is a Python project designed to crawl data from the [HAL (Hyper Articles en Ligne) repository](https://hal.science/). It provides functionalities to fetch data from HAL and to process it for further analysis.

The latest dump can be found on [HuggingFace](https://huggingface.co/datasets/Madjakul/HALvest).


## Features

- [**fetch_data.py**](fetch_data.py): This script fetches data from HAL using specified criterias.
- [**merge_data.py**](merge_data.py): This script is used for post-processing the fetched data.
- [**enrich_data.py**](enrich_data.py): This script adds new keys to the merged data.
- [**filter_data.py**](filter_data.py): This script removes gibberish documents.


## Requirements

You will need Python > 3.8 and an internet connection.


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

It's easier to modify the files [`scripts/fetch_data.sh`](scripts/fetch_data.sh), [`scripts/merge_data.sh`](scripts/merge_data.sh), [`scripts/enrich_data.sh`](scripts/enrich_data.sh) and [`scripts/filter_data.sh`](scripts/filter_data.sh) at need and launch them. However one can launch directly the Python scripts with the correct arguments as we will see below.


### Fetching Data

This scripts passes a query to HAL's API and fetch all the open papers before storing them in a JSON file. The fetched data is only comprise of papers' metadatas.

```js
[
    {
        "halid": "02975689",
        "lang": "ar",
        "domain": [ "math.math-ho", "shs.edu" ],
        "timestamp": "2024/03/04 16:36:13",
        "year": "2020",
        "url": "https://hal.science/hal-02975689/file/DAD-TGP_Encyclopedia_Arabic.pdf"
    },
    ...
]
```

```
>>> python3 fetch_data.py -h
usage: fetch_data.py [-h] [--query [QUERY]] [--from_date FROM_DATE] [--from_hour FROM_HOUR] [--to_date TO_DATE] [--to_hour TO_HOUR] --pdf PDF --response_dir RESPONSE_DIR [--pdf_dir [PDF_DIR]] [--num_chunks [NUM_CHUNKS]]

Arguments used to fetch data.

options:
  -h, --help            show this help message and exit
  --query [QUERY]       Query used to request APIs.
  --from_date FROM_DATE
                        Minimum submition date of documents.
  --from_hour FROM_HOUR
                        Minimum submition hour of documents.
  --to_date TO_DATE     Maximum submition date of documents.
  --to_hour TO_HOUR     Maximum submition hour of documents.
  --pdf PDF             Set to `true` if you want to download the PDFs.
  --response_dir RESPONSE_DIR
                        Target directory used to store fetched data.
  --pdf_dir [PDF_DIR]   Target directory used to store the PDFs.
  --num_chunks [NUM_CHUNKS]
                        Number of semaphores for the PDF downloader.

```


### Post-process Data

This script merges the fetched metadatas with the generated text from GROBID and harvesting. The output are compressed JSON files sorted by language.


```
>>> python3 merge_data.py
usage: merge_data.py [-h] --js_dir_path JS_DIR_PATH --txts_dir_path TXTS_DIR_PATH --output_dir_path OUTPUT_DIR_PATH --version VERSION

Arguments used to fetch data.

options:
  -h, --help            show this help message and exit
  --js_dir_path JS_DIR_PATH
                        Folder containing fetched data.
  --txts_dir_path TXTS_DIR_PATH
                        Folder containing the txt files.
  --output_dir_path OUTPUT_DIR_PATH
                        Final folder containing the processed data for HuggingFace.
  --version VERSION     Version of the dump starting at '1.0'.
```


### Enrich Data

This script adds new keys to the merged data.

```
>>> python3 enrich_data.py -h
usage: enrich_data.py [-h] [--dataset_checkpoint DATASET_CHECKPOINT] [--cache_dir_path [CACHE_DIR_PATH]] [--dataset_config_path DATASET_CONFIG_PATH] [--download_models DOWNLOAD_MODELS] [--kenlm_dir_path KENLM_DIR_PATH] [--num_proc NUM_PROC]
                      [--batch_size BATCH_SIZE] [--output_dir_path OUTPUT_DIR_PATH] [--tokenizer_checkpoint [TOKENIZER_CHECKPOINT]] [--use_fast [USE_FAST]] [--load_from_cache_file [LOAD_FROM_CACHE_FILE]] --version VERSION

Download Sentencepiece and KenLM models for supported languages.

options:
  -h, --help            show this help message and exit
  --dataset_checkpoint DATASET_CHECKPOINT
                        Name of the HuggingFace dataset to be processed.
  --cache_dir_path [CACHE_DIR_PATH]
                        Path to the HuggingFace cache directory.
  --dataset_config_path DATASET_CONFIG_PATH
                        Path to the txt file containing the dataset configs to process.
  --download_models DOWNLOAD_MODELS
                        Set to `true` if you want to download the KenLM models.
  --kenlm_dir_path KENLM_DIR_PATH
                        Path to the directory containing the sentencepiece and kenlm models.
  --num_proc NUM_PROC   Number of processes to use for processing the dataset.
  --batch_size BATCH_SIZE
                        Number of documents loaded per proc.
  --output_dir_path OUTPUT_DIR_PATH
                        Path to the directory where the processed dataset will be saved.
  --tokenizer_checkpoint [TOKENIZER_CHECKPOINT]
                        Name of the HuggingFace tokenizer model to be used.
  --use_fast [USE_FAST]
                        Set to `true` if you want to use the Ruste-based tokenizer from HF.
  --load_from_cache_file [LOAD_FROM_CACHE_FILE]
                        Set to `true` if you if some of the enriching functions have been altered.
  --version VERSION     Version of the dump starting at '1.0'.
```


### Filter Data

This script filters out raw data out of the gibberish documents

```
>>> python3 filter_data.py -h
usage: filter_data.py [-h] [--dataset_checkpoint DATASET_CHECKPOINT] [--cache_dir_path [CACHE_DIR_PATH]] [--dataset_config_path DATASET_CONFIG_PATH] [--num_proc NUM_PROC] [--batch_size BATCH_SIZE] [--output_dir_path OUTPUT_DIR_PATH]
                      [--load_from_cache_file [LOAD_FROM_CACHE_FILE]] --version VERSION

Argument used to filter the dataset.

options:
  -h, --help            show this help message and exit
  --dataset_checkpoint DATASET_CHECKPOINT
                        Name of the HuggingFace dataset to be processed.
  --cache_dir_path [CACHE_DIR_PATH]
                        Path to the HuggingFace cache directory.
  --dataset_config_path DATASET_CONFIG_PATH
                        Path to the txt file containing the dataset configs to process.
  --num_proc NUM_PROC   Number of processes to use for processing the dataset.
  --batch_size BATCH_SIZE
                        Number of documents loaded per proc.
  --output_dir_path OUTPUT_DIR_PATH
                        Path to the directory where the processed dataset will be saved.
  --load_from_cache_file [LOAD_FROM_CACHE_FILE]
                        Set to `true` if you if some of the enriching functions have been altered.
  --version VERSION     Version of the dump starting at '1.0'.
```


## Citation

To cite HALvesting/HALvest:

```bib
@misc{kulumba2024harvestingtextualstructureddata,
      title={Harvesting Textual and Structured Data from the HAL Publication Repository}, 
      author={Francis Kulumba and Wissam Antoun and Guillaume Vimont and Laurent Romary},
      year={2024},
      eprint={2407.20595},
      archivePrefix={arXiv},
      primaryClass={cs.DL},
      url={https://arxiv.org/abs/2407.20595}, 
}
```


## Acknowledgement

The code and the dataset have been built upon the following work:

```
GROBID: A machine learning software for extracting information from scholarly documents
https://github.com/kermitt2/grobid

harvesting: Collection of parsers for scientific data
```


## License

This project is licensed under the [Apache License 2.0](LICENSE).
