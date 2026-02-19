#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${WSGI_ENV_FILE:-$SCRIPT_DIR/.env.wsgi}"
PID_FILE="$SCRIPT_DIR/.gunicorn/gunicorn.pid"

if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi

if [ -f "$PID_FILE" ]; then
  pid="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" || true
    sleep 1
  fi
fi

pkill -f 'gunicorn.*wsgi:app' 2>/dev/null || true
mkdir -p "$SCRIPT_DIR/.gunicorn"

if [ -x "$SCRIPT_DIR/.venv/bin/gunicorn" ]; then
  GUNICORN_BIN="$SCRIPT_DIR/.venv/bin/gunicorn"
elif [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/gunicorn" ]; then
  GUNICORN_BIN="$VIRTUAL_ENV/bin/gunicorn"
elif command -v gunicorn >/dev/null 2>&1; then
  GUNICORN_BIN="$(command -v gunicorn)"
else
  echo "Gunicorn not found in .venv, VIRTUAL_ENV, or PATH." >&2
  echo "Please install gunicorn in the runtime environment." >&2
  exit 1
fi

"$GUNICORN_BIN" -c "$SCRIPT_DIR/gunicorn.py" wsgi:app
