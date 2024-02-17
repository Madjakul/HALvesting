#!/bin/bash

PROJECT_ROOT=$(dirname "$(readlink -f "$0")")/..    # Do not modify
DATA_ROOT=$PROJECT_ROOT/data                        # Do not modify

# ************************** Customizable Arguments ***************************

QUERY="*"

# -------------------------- Optional Arguments -------------------------------
FROM_DATE="2001-01-01"
FROM_HOUR="00:00:00"
TO_DATE="2001-12-31"
TO_HOUR="23:59:59"
PDF=1
# -----------------------------------------------------------------------------

# *****************************************************************************


center() {
  termwidth="$(tput cols)"
  padding="$(printf '%0.1s' ={1..500})"
  printf '%*.*s %s %*.*s\n' 0 "$(((termwidth-2-${#1})/2))" "$padding" "$1" 0 "$(((termwidth-1-${#1})/2))" "$padding"
}

mkdir logs "$DATA_ROOT"/pdfs


cmd=( python3 fetch_data.py )

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
    cmd+=( --pdf )
fi


center "Fetching Data from HAL"
"${cmd[@]}"
center "Done"

