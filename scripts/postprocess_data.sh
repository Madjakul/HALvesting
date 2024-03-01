#!/bin/bash

PROJECT_ROOT=$(dirname "$(readlink -f "$0")")/..    # Do not modify
DATA_ROOT=$PROJECT_ROOT/data                        # Do not modify

# ************************** Customizable Arguments ***************************

JS_FOLDER="responses_0"
TXT_FOLDER="txts.zip"
HF_FOLDER="hf"

# *****************************************************************************


center() {
  termwidth="$(tput cols)"
  padding="$(printf '%0.1s' ={1..500})"
  printf '%*.*s %s %*.*s\n' 0 "$(((termwidth-2-${#1})/2))" "$padding" "$1" 0 "$(((termwidth-1-${#1})/2))" "$padding"
}

mkdir logs

cmd=( python3 postprocess_data.py \
  --js_folder "$DATA_ROOT/$JS_FOLDER" \
  --txt_folder "$DATA_ROOT/$TXT_FOLDER" \
  --hf_folder "$DATA_ROOT/$HF_FOLDER" )

center "Generating Data"
"${cmd[@]}"
center "Done"
