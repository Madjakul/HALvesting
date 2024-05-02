#!/bin/bash

PROJECT_ROOT=$(dirname "$(readlink -f "$0")")/..    # Do not modify
DATA_ROOT=$PROJECT_ROOT/data                        # Do not modify

# ************************** Customizable Arguments ************************************

DATASET_CHECKPOINT="Madjakul/HALvest"
DATASET_CONFIG_PATH="$DATA_ROOT/configs.txt"

DOWNLOAD_MODELS=true
KENLM_DIR_PATH="$PROJECT_ROOT/tmp/kelm"

NUM_PROC=24
BATCH_SIZE=1000

OUTPUT_DIR_PATH="$DATA_ROOT/$DATASET_CHECKPOINT"
VERSION="1.0"

# -------------------------------- Optional Arguments ----------------------------------

# CACHE_DIR_PATH="/local"

# TOKENIZER_CHECKPOINT="google/mt5-base"
# USE_FAST=true
# LOAD_FROM_CACHE_FILE=true

# --------------------------------------------------------------------------------------

# **************************************************************************************


cmd=( python3 "$PROJECT_ROOT/enrich_data.py" \
  --dataset_checkpoint "${DATASET_CHECKPOINT:-Madjakul/HALvest-R}" \
  --dataset_config_path "${DATASET_CONFIG_PATH:-$DATA_ROOT/$DATA_ROOT/configs.txt}" \
  --download_models "$DOWNLOAD_MODELS" \
  --kenlm_dir_path "${KENLM_DIR_PATH:-$PROJECT_ROOT/tmp/kenlm}" \
  --num_proc "$NUM_PROC" \
  --batch_size "$BATCH_SIZE" \
  --output_dir_path "${OUTPUT_DIR_PATH:-$DATA_ROOT/$DATASET_CHECKPOINT}" \
  --version "$VERSION" \
  --load_from_cache_file "${LOAD_FROM_CACHE_FILE:-false}" )

if [[ -v CACHE_DIR_PATH ]]; then
  cmd+=( --cache_dir "$CACHE_DIR_PATH" )
fi

if [[ -v TOKENIZER_CHECKPOINT ]]; then
  cmd+=( --tokenizer_checkpoint "$TOKENIZER_CHECKPOINT" \
    --use_fast "${USE_FAST:-false}" )
fi
"${cmd[@]}"
