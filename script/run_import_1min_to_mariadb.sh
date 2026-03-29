#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMPORT_SCRIPT_HOST="${ROOT_DIR}/script/import_1min_to_mariadb.py"

CONTAINER_NAME="${CONTAINER_NAME:-backquant-import-1min}"
BACKEND_CONTAINER="${BACKEND_CONTAINER:-backquant-backend-1}"
IMAGE="${IMAGE:-backquant-backend}"
NETWORK="${NETWORK:-backquant_default}"
DATA_DIR="${DATA_DIR:-/root/download/1min}"

get_backend_env() {
  local key="$1"

  docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' "$BACKEND_CONTAINER" 2>/dev/null \
    | awk -F= -v key="$key" '$1 == key { sub(/^[^=]*=/, ""); print; exit }'
}

DB_HOST="${DB_HOST:-$(get_backend_env DB_HOST || true)}"
DB_PORT="${DB_PORT:-$(get_backend_env DB_PORT || true)}"
DB_NAME="${DB_NAME:-$(get_backend_env DB_NAME || true)}"
DB_USER="${DB_USER:-$(get_backend_env DB_USER || true)}"
DB_PASSWORD="${DB_PASSWORD:-$(get_backend_env DB_PASSWORD || true)}"
DB_TABLE="${DB_TABLE:-$(get_backend_env DB_TABLE || true)}"

DB_HOST="${DB_HOST:-mariadb}"
DB_PORT="${DB_PORT:-3306}"
DB_NAME="${DB_NAME:-backquant}"
DB_USER="${DB_USER:-backquant_user}"
DB_PASSWORD="${DB_PASSWORD:-backquant_pass}"
DB_TABLE="${DB_TABLE:-dbbardata}"

TRUNCATE_BEFORE_IMPORT="${TRUNCATE_BEFORE_IMPORT:-0}"
REPLACE_DUPLICATES="${REPLACE_DUPLICATES:-0}"
MIN_CONTRACT_YEAR="${MIN_CONTRACT_YEAR:-2015}"
INTERVAL_VALUE="${INTERVAL_VALUE:-1m}"
CSV_ENCODING="${CSV_ENCODING:-utf-8}"

# 默认只导入这些品种。传入 all 时改为全量导入。
IMPORT_PRODUCT_CODES=(
  rb
  hc
  i
  jm
  j
)

IMPORT_MODE="${1:-selected}"
PRODUCT_CODES=""

if [[ "$IMPORT_MODE" == "all" ]]; then
  PRODUCT_CODES_LABEL="all"
elif [[ "$IMPORT_MODE" == "selected" ]]; then
  PRODUCT_CODES="$(IFS=,; echo "${IMPORT_PRODUCT_CODES[*]}")"
  PRODUCT_CODES_LABEL="$PRODUCT_CODES"
else
  echo "Usage: $0 [all]" >&2
  exit 1
fi

if [[ ! -d "$DATA_DIR" ]]; then
  echo "DATA_DIR not found: $DATA_DIR" >&2
  exit 1
fi

if [[ ! -f "$IMPORT_SCRIPT_HOST" ]]; then
  echo "Import script not found: $IMPORT_SCRIPT_HOST" >&2
  exit 1
fi

if docker ps -a --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"; then
  echo "Removing existing container: $CONTAINER_NAME"
  docker rm -f "$CONTAINER_NAME" >/dev/null
fi

echo "Starting container: $CONTAINER_NAME"
echo "Data dir: $DATA_DIR"
echo "DB: $DB_HOST:$DB_PORT/$DB_NAME table=$DB_TABLE user=$DB_USER"
echo "Product codes: $PRODUCT_CODES_LABEL"

docker_args=(
  run
  -d
  --name "$CONTAINER_NAME"
  --network "$NETWORK"
  -v "$DATA_DIR:$DATA_DIR:ro"
  -v "$ROOT_DIR/script:/hostscript:ro"
  -e "DATA_DIR=$DATA_DIR"
  -e "DB_HOST=$DB_HOST"
  -e "DB_PORT=$DB_PORT"
  -e "DB_NAME=$DB_NAME"
  -e "DB_USER=$DB_USER"
  -e "DB_PASSWORD=$DB_PASSWORD"
  -e "DB_TABLE=$DB_TABLE"
  -e "TRUNCATE_BEFORE_IMPORT=$TRUNCATE_BEFORE_IMPORT"
  -e "REPLACE_DUPLICATES=$REPLACE_DUPLICATES"
  -e "MIN_CONTRACT_YEAR=$MIN_CONTRACT_YEAR"
  -e "INTERVAL_VALUE=$INTERVAL_VALUE"
  -e "CSV_ENCODING=$CSV_ENCODING"
)

if [[ -n "$PRODUCT_CODES" ]]; then
  docker_args+=(-e "PRODUCT_CODES=$PRODUCT_CODES")
fi

docker "${docker_args[@]}" \
  --entrypoint python \
  "$IMAGE" \
  /hostscript/import_1min_to_mariadb.py

echo "Follow logs with: docker logs -f $CONTAINER_NAME"
