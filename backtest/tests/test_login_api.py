import unittest
from datetime import datetime, timezone

import jwt
from flask import Flask

from app.api.login_api import bp_login


class LoginApiTestCase(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config.update(
            LOCAL_AUTH_MOBILE="13800138000",
            LOCAL_AUTH_PASSWORD="pass123456",
            LOCAL_AUTH_USER_ID=7,
            LOCAL_AUTH_IS_ADMIN=True,
            JWT_EXPIRES_HOURS=2,
            SECRET_KEY="test-secret",
            TESTING=True,
        )
        app.register_blueprint(bp_login)
        self.app = app
        self.client = app.test_client()

    def test_login_success_returns_token_userid_and_is_admin(self):
        resp = self.client.post(
            "/api/login",
            data={"mobile": "13800138000", "password": "pass123456"},
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertIn("token", payload)
        self.assertEqual(payload["userid"], 7)
        self.assertTrue(payload["is_admin"])

        decoded = jwt.decode(payload["token"], "test-secret", algorithms=["HS256"])
        self.assertEqual(decoded["user_id"], 7)
        self.assertTrue(decoded["is_admin"])
        self.assertGreater(decoded["exp"], int(datetime.now(timezone.utc).timestamp()))

    def test_login_rejects_invalid_credentials(self):
        resp = self.client.post(
            "/api/login",
            data={"mobile": "13800138000", "password": "wrong"},
        )
        self.assertEqual(resp.status_code, 401)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "UNAUTHORIZED")

    def test_login_requires_mobile_and_password(self):
        resp = self.client.post("/api/login", data={"mobile": "13800138000"})
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "INVALID_ARGUMENT")


if __name__ == "__main__":
    unittest.main()
