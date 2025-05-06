#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 GET_CONN POST_CONN [--db-name NAME] [--boat-side {b|t}] [--filter-columns a,b,c]

  GET_CONN           REST host:port to GET data from
  POST_CONN          REST host:port to PUT data to
  --db-name NAME     logical database (default: anotherpeak)
  --boat-side {b|t}  b→starboard/Helios_B, t→port/Helios_T (default: b)
  --filter-columns   comma-separated keys to include (default: all)
EOF
  exit 1
}

# -- Require at least two positional args
if [ "$#" -lt 2 ]; then usage; fi

# -- Positional
GET_CONN="$1"; POST_CONN="$2"; shift 2

# -- Defaults
DB_NAME="anotherpeak"
BOAT_SIDE="b"
IFS=',' read -r -a FILTER_COLUMNS <<< ""   # empty list

# -- Parse opts
while [ "$#" -gt 0 ]; do
  case "$1" in
    --db-name)           DB_NAME="$2"; shift 2 ;;
    --boat-side)         BOAT_SIDE="$2"; shift 2 ;;
    --filter-columns)    IFS=',' read -r -a FILTER_COLUMNS <<< "$2"; shift 2 ;;
    -h|--help)           usage ;;
    *) echo "Unknown option: $1"; usage ;;
  esac
done

# -- Map boat side to table & label
declare -A TABLE_MAP=( ["b"]="Helios_B" ["t"]="Helios_T" )
declare -A SIDE_MAP=(  ["b"]="starboard" ["t"]="port"   )

TABLE_NAME="${TABLE_MAP[$BOAT_SIDE]}"
SIDE_LABEL="${SIDE_MAP[$BOAT_SIDE]}"

# -- Fetch data (error out if non‑2xx)
RAW_JSON=$(curl -sS -f "http://$GET_CONN")

# -- Build payloads via jq
if [ "${#FILTER_COLUMNS[@]}" -eq 0 ]; then
  # no filtering: just append conn & boat_side
  PAYLOADS=$(jq --arg conn "$GET_CONN" --arg bs "$SIDE_LABEL" '
    if type=="array"
      then map(. + {conn:$conn, boat_side:$bs})
      else [ . + {conn:$conn, boat_side:$bs} ]
    end' <<<"$RAW_JSON")
else
  # with filtering: pick only requested keys
  # build a jq array of field names
  jq_fields=$(printf '%s\n' "${FILTER_COLUMNS[@]}" | jq -R . | jq -s .)
  PAYLOADS=$(jq --arg conn "$GET_CONN" --arg bs "$SIDE_LABEL" \
                --argjson cols "$jq_fields" '
    def pick_fields:
      reduce cols[] as $f ({}; if has($f) then . + { ($f): .[$f] } else . end);
    if type=="array"
      then map(pick_fields + {conn:$conn, boat_side:$bs})
      else [ (pick_fields + {conn:$conn, boat_side:$bs}) ]
    end' <<<"$RAW_JSON")
fi

# -- Publish payloads
curl -sS -f -X PUT "http://$POST_CONN" \
     -H "Content-Type: application/json" \
     -H "type: json" \
     -H "dbms: $DB_NAME" \
     -H "table: $TABLE_NAME" \
     -H "mode: streaming" \
     --data-raw "$PAYLOADS"

echo "✅ Successfully synced to $POST_CONN → DB:$DB_NAME Table:$TABLE_NAME"
