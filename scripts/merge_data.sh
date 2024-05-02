#!/bin/bash

PROJECT_ROOT=$(dirname "$(readlink -f "$0")")/..    # Do not modify
DATA_ROOT=$PROJECT_ROOT/data                        # Do not modify

# ************************** Customizable Arguments ***************************

JS_DIR_PATH="responses_0"
TXTS_DIR_PATH="txts.zip"
OUTPUT_DIR_PATH="hf"
VERSION="1.0"

# *****************************************************************************


cmd=( python3 "$PROJECT_ROOT/merge_data.py" \
  --js_dir_path "$DATA_ROOT/$JS_DIR_PATH" \
  --txts_dir_path "$DATA_ROOT/$TXTS_DIR_PATH" \
  --output_dir_path "$DATA_ROOT/$OUTPUT_DIR_PATH" \
  --version "$VERSION" )
"${cmd[@]}"
