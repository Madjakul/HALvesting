#!/bin/bash

PROJECT_ROOT=$(dirname "$(readlink -f "$0")")/..    # Do not modify
DATA_ROOT=$PROJECT_ROOT/data                        # Do not modify

# ************************** Customizable Arguments ***************************

LANGS="all"
DATASET_NAME="Madjakul/HALvest"
DATASET_CONFIG_NAME="ar,az"
FASTTEXT_MODEL_FILE="$PROJECT_ROOT/tmp/fasttext"
HF_MODEL_NAME="google/mt5-small"
DATASET_DIR_PATH="$DATA_ROOT/$DATASET_NAME"
NUM_PROC=1

# -------------------------- Optional Arguments -------------------------------
OUTPUT_DIR_PATH="$PROJECT_ROOT/tmp/kelm"
# -----------------------------------------------------------------------------

# *****************************************************************************


center() {
  termwidth="$(tput cols)"
  padding="$(printf '%0.1s' ={1..500})"
  printf '%*.*s %s %*.*s\n' 0 "$(((termwidth-2-${#1})/2))" "$padding" "$1" 0 "$(((termwidth-1-${#1})/2))" "$padding"
}

mkdir logs


cmd=( python3 "$PROJECT_ROOT/fetch_data.py" \
  --response_dir "${RESPONSE_DIR:-"$DATA_ROOT/pdfs"}" )

if [[ -v QUERY ]]; then
  cmd+=( --query "$QUERY" )
fi
if [[ -v FROM_DATE ]]; then
  cmd+=( --from_date "$FROM_DATE" )
fi
if [[ -v FROM_HOUR ]]; then
  cmd+=( --from_hour "$FROM_HOUR" )
fi
if [[ -v TO_DATE ]]; then
  cmd+=( --to_date "$TO_DATE" )
fi
if [[ -v TO_HOUR ]]; then
  cmd+=( --to_hour "$TO_HOUR" )
fi
if [[ -v PDF ]]; then
  cmd+=( --pdf \
    --pdf_dir "$PDF_DIR" \
    --num_chunks $NUM_CHUNKS )
fi


center "Fetching Data from HAL"
"${cmd[@]}"
center "Done"
