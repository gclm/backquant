from __future__ import annotations

import datetime as dt
import base64
import hashlib
import hmac
import json
from functools import wraps

from flask import current_app, g, jsonify, request


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _unauthorized_response(message: str):
    return jsonify({"ok": False, "error": {"code": "UNAUTHORIZED", "message": message}}), 401


class ExpiredSignatureError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise InvalidTokenError("invalid token")
    padding = "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode((value + padding).encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise InvalidTokenError("invalid token") from exc


def _jwt_signing_input(header: dict, payload: dict) -> str:
    header_json = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return f"{_b64url_encode(header_json)}.{_b64url_encode(payload_json)}"


def _encode_hs256(payload: dict, secret_key: str) -> str:
    signing_input = _jwt_signing_input({"alg": "HS256", "typ": "JWT"}, payload)
    signature = hmac.new(
        secret_key.encode("utf-8"),
        signing_input.encode("ascii"),
        digestmod=hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def _decode_hs256(token: str, secret_key: str) -> dict:
    if not isinstance(token, str):
        raise InvalidTokenError("invalid token")
    parts = token.split(".")
    if len(parts) != 3:
        raise InvalidTokenError("invalid token")
    header_b64, payload_b64, signature_b64 = parts

    try:
        header = json.loads(_b64url_decode(header_b64).decode("utf-8"))
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise InvalidTokenError("invalid token") from exc

    if not isinstance(header, dict) or header.get("alg") != "HS256":
        raise InvalidTokenError("invalid token")
    if not isinstance(payload, dict):
        raise InvalidTokenError("invalid token")

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    expected_signature = hmac.new(
        secret_key.encode("utf-8"),
        signing_input,
        digestmod=hashlib.sha256,
    ).digest()
    provided_signature = _b64url_decode(signature_b64)
    if not hmac.compare_digest(provided_signature, expected_signature):
        raise InvalidTokenError("invalid token")

    exp_raw = payload.get("exp")
    try:
        exp = int(exp_raw)
    except (TypeError, ValueError) as exc:
        raise InvalidTokenError("invalid token") from exc
    now = int(dt.datetime.now(dt.timezone.utc).timestamp())
    if now >= exp:
        raise ExpiredSignatureError("token has expired")

    return payload


def generate_auth_token(*, user_id: int | str, is_admin: bool = False) -> str:
    expires_hours = int(current_app.config.get("JWT_EXPIRES_HOURS", 24))
    expires_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=max(expires_hours, 1))
    payload = {
        "user_id": user_id,
        "is_admin": _as_bool(is_admin),
        "exp": int(expires_at.timestamp()),
    }
    return _encode_hs256(payload, str(current_app.config["SECRET_KEY"]))


def decode_auth_token(token: str) -> dict:
    return _decode_hs256(token, str(current_app.config["SECRET_KEY"]))


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = (request.headers.get("Authorization") or "").strip()
        if not token:
            return _unauthorized_response("token is missing")
        if token.lower().startswith("bearer "):
            token = token[7:].strip()
            if not token:
                return _unauthorized_response("token is missing")

        try:
            payload = decode_auth_token(token)
        except ExpiredSignatureError:
            return _unauthorized_response("token has expired")
        except InvalidTokenError:
            return _unauthorized_response("invalid token")

        user_id = payload.get("user_id")
        if user_id in (None, ""):
            return _unauthorized_response("invalid token")

        g.user_id = user_id
        g.is_admin = _as_bool(payload.get("is_admin", False))
        return func(*args, **kwargs)

    return wrapper
