#!/bin/bash

PROJECT_ROOT=$(dirname "$(readlink -f "$0")")/..    # Do not modify
DATA_ROOT=$PROJECT_ROOT/data                        # Do not modify

# ************************** Customizable Arguments ************************************

DATASET_CHECKPOINT="Madjakul/HALvest-R"
DATASET_CONFIG_PATH="$DATA_ROOT/configs.txt"

NUM_PROC=24
BATCH_SIZE=1000

OUTPUT_DIR_PATH="$DATA_ROOT/Madjakul/HALvest"
VERSION="1.0"

# -------------------------------- Optional Arguments ----------------------------------

CACHE_DIR_PATH="/local"

# LOAD_FROM_CACHE_FILE=true

# --------------------------------------------------------------------------------------

# **************************************************************************************


cmd=( python3 "$PROJECT_ROOT/filter_data.py" \
  --dataset_checkpoint "${DATASET_CHECKPOINT:-Madjakul/HALvest-R}" \
  --dataset_config_path "${DATASET_CONFIG_PATH:-$DATA_ROOT/$DATA_ROOT/configs.txt}" \
  --num_proc "$NUM_PROC" \
  --batch_size "$BATCH_SIZE" \
  --output_dir_path "${OUTPUT_DIR_PATH:-$DATA_ROOT/$DATASET_CHECKPOINT}" \
  --version "$VERSION" \
  --load_from_cache_file "${LOAD_FROM_CACHE_FILE:-false}" )

if [[ -v CACHE_DIR_PATH ]]; then
  cmd+=( --cache_dir_path "$CACHE_DIR_PATH" )
fi
"${cmd[@]}"
