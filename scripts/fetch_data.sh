#!/bin/bash

PROJECT_ROOT=$(dirname "$(readlink -f "$0")")/..    # Do not modify
DATA_ROOT=$PROJECT_ROOT/data                        # Do not modify

# ******************************* Customizable Arguments *******************************

RESPONSE_DIR="$DATA_ROOT/responses_4"

# ------------------------------- Optional Arguments -----------------------------------
QUERY="*"
FROM_DATE="2024-02-01"
FROM_HOUR="00:00:00"
TO_DATE="2024-05-31"
TO_HOUR="23:59:59"

PDF=false
PDF_DIR="$DATA_ROOT/pdfs"   # Mandatory if PDF is true
NUM_CHUNKS=100              # mandatory if PDF is true
# --------------------------------------------------------------------------------------

# **************************************************************************************


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
cmd+=( --pdf "$PDF" \
    --pdf_dir "$PDF_DIR" \
    --num_chunks "$NUM_CHUNKS" )

"${cmd[@]}"
