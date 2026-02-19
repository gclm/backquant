#!/opt/anaconda3/bin/python3
#coding: utf8

import os
from pathlib import Path


def _load_env_file() -> None:
    env_path = os.environ.get("WSGI_ENV_FILE")
    if env_path:
        target = Path(env_path).expanduser()
    else:
        target = Path(__file__).resolve().parent / ".env.wsgi"

    if not target.exists():
        return

    for line in target.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        os.environ.setdefault(key, value)


# Ensure app config can read env vars before importing app modules.
_load_env_file()

from app import create_app
from app.config import CONFIG_ENV

app = create_app(CONFIG_ENV)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=54321)
