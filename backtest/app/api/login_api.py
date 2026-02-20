from __future__ import annotations

import hmac
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from app.auth import generate_auth_token

bp_login = Blueprint("bp_login", __name__)

_BUNDLE_REQUIRED_FILES = ("future_info.json", "instruments.pk", "trading_dates.npy")


def _error_response(http_status: int, code: str, message: str):
    return jsonify({"error": {"code": code, "message": message}}), http_status


def _as_admin_flag(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _parse_login_form() -> tuple[str, str]:
    data = request.form.to_dict() if request.form else {}
    if not data:
        data = request.get_json(silent=True) or {}
    mobile = data.get("mobile")
    password = data.get("password")
    mobile = mobile.strip() if isinstance(mobile, str) else ""
    password = password if isinstance(password, str) else ""
    return mobile, password


def _invalid_credentials():
    return _error_response(401, "UNAUTHORIZED", "invalid credentials")

def _bundle_is_ready(bundle_path: Path) -> bool:
    if not bundle_path.exists() or not bundle_path.is_dir():
        return False
    try:
        if not any(bundle_path.iterdir()):
            return False
    except OSError:
        return False
    for filename in _BUNDLE_REQUIRED_FILES:
        candidate = bundle_path / filename
        try:
            if not candidate.is_file() or candidate.stat().st_size <= 0:
                return False
        except OSError:
            return False
    return True


def _verify_bcrypt_password(password: str, password_hash: str) -> tuple[bool, tuple | None]:
    try:
        import bcrypt
    except ImportError:
        return False, _error_response(500, "AUTH_CONFIG_ERROR", "bcrypt is not installed")

    try:
        ok = bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False, _error_response(500, "AUTH_CONFIG_ERROR", "bcrypt hash is invalid")
    return ok, None


def _local_login(mobile: str, password: str):
    expected_mobile = str(current_app.config.get("LOCAL_AUTH_MOBILE", "") or "").strip()
    password_hash = str(current_app.config.get("LOCAL_AUTH_PASSWORD_HASH", "") or "").strip()
    plain_password = str(current_app.config.get("LOCAL_AUTH_PASSWORD", "") or "")
    if not expected_mobile or (not password_hash and not plain_password):
        return _error_response(500, "AUTH_CONFIG_ERROR", "local auth config is incomplete")

    if not hmac.compare_digest(mobile, expected_mobile):
        return _invalid_credentials()

    if password_hash:
        ok, err_resp = _verify_bcrypt_password(password, password_hash)
        if err_resp:
            return err_resp
        if not ok:
            return _invalid_credentials()
    elif not hmac.compare_digest(password, plain_password):
        return _invalid_credentials()

    user_id = int(current_app.config.get("LOCAL_AUTH_USER_ID", 1))
    is_admin = _as_admin_flag(current_app.config.get("LOCAL_AUTH_IS_ADMIN", True))
    token = generate_auth_token(user_id=user_id, is_admin=is_admin)
    return jsonify({"token": token, "userid": user_id, "is_admin": is_admin}), 200


@bp_login.post("/api/login")
def api_login():
    mobile, password = _parse_login_form()
    if not mobile or not password:
        return _error_response(400, "INVALID_ARGUMENT", "mobile and password are required")
    bundle_path = Path(current_app.config.get("RQALPHA_BUNDLE_PATH") or "").expanduser()
    if not bundle_path or not _bundle_is_ready(bundle_path):
        return _error_response(503, "BUNDLE_NOT_READY", "bundle is downloading")
    return _local_login(mobile, password)
