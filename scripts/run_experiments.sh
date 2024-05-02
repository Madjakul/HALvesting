#!/bin/bash

PROJECT_ROOT=$(dirname "$(readlink -f "$0")")/..    # Do not modify
DATA_ROOT=$PROJECT_ROOT/data                        # Do not modify

# ************************** Customizable Arguments ************************************

DATASET_CHECKPOINT="Madjakul/HALvest"
DATASET_CONFIG_PATH="$DATA_ROOT/configs.txt"
COUNT_RAW_TOKENS=false

OUTPUT_DIR_PATH="$PROJECT_ROOT/tmp/experiments2_out"
BATCH_SIZE=1000
NUM_PROC=24

# -------------------------------- Optional Arguments ----------------------------------

# CACHE_DIR_PATH="/local"

# --------------------------------------------------------------------------------------

# **************************************************************************************


cmd=( python3 "$PROJECT_ROOT/run_experiments.py" \
  --dataset_checkpoint "${DATASET_CHECKPOINT:-Madjakul/HALvest-R}" \
  --dataset_config_path "${DATASET_CONFIG_PATH:-$DATA_ROOT/$DATA_ROOT/configs.txt}" \
  --output_dir_path "${OUTPUT_DIR_PATH:-$DATA_ROOT/$DATASET_CHECKPOINT}" \
  --count_raw_tokens "$COUNT_RAW_TOKENS" \
  --batch_size "$BATCH_SIZE" \
  --num_proc "$NUM_PROC" )

if [[ -v CACHE_DIR_PATH ]]; then
  cmd+=( --cache_dir_path "$CACHE_DIR_PATH" )
fi
"${cmd[@]}"
