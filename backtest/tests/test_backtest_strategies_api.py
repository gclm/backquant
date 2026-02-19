import os
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
from unittest.mock import patch

import jwt
from flask import Flask

from app.api.backtest_api import bp_backtest
from app.backtest.services.runner import load_strategy, save_strategy, update_job_index, write_job_index


class BacktestStrategiesApiTestCase(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.base_dir = self._tmpdir.name

        app = Flask(__name__)
        app.config.update(
            BACKTEST_BASE_DIR=self.base_dir,
            RQALPHA_BUNDLE_PATH="/tmp",
            BACKTEST_TIMEOUT=1,
            BACKTEST_KEEP_DAYS=30,
            SECRET_KEY="test-secret",
            TESTING=True,
        )
        app.register_blueprint(bp_backtest)
        self.app = app
        self.client = app.test_client()

    def tearDown(self):
        self._tmpdir.cleanup()

    def _set_strategy(self, strategy_id: str, code: str, mtime: int) -> None:
        with self.app.app_context():
            path = save_strategy(strategy_id, code)
        os.utime(path, (mtime, mtime))

    def _seed_strategy_reference(self, strategy_id: str, job_id: str = "job_ref_demo") -> None:
        job_dir = Path(self.base_dir) / "runs" / "2026-02-16" / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        with self.app.app_context():
            write_job_index(job_id, job_dir)
            update_job_index(
                job_id,
                strategy_id=strategy_id,
                status="FINISHED",
                created_at="2026-02-16T10:00:00Z",
                updated_at="2026-02-16T10:30:00Z",
                params={},
                error=None,
            )

    def _auth_headers(self, *, is_admin: bool = True) -> dict:
        token = jwt.encode(
            {"user_id": 1, "is_admin": is_admin, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            self.app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return {"Authorization": token}

    def test_list_strategies_empty(self):
        resp = self.client.get("/api/backtest/strategies", headers=self._auth_headers())
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["message"], "ok")
        self.assertEqual(payload["data"], {"strategies": [], "total": 0})

    def test_list_strategies_sorted_by_updated_at_desc(self):
        self._set_strategy("alpha", "def init(context):\n    pass\n", 1700000000)
        self._set_strategy("beta", "def init(context):\n    pass\n", 1700000200)
        self._set_strategy("gamma", "def init(context):\n    pass\n", 1700000100)

        resp = self.client.get("/api/backtest/strategies", headers=self._auth_headers())
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload["code"], 200)
        data = payload["data"]
        self.assertEqual(data["total"], 3)
        self.assertEqual([item["id"] for item in data["strategies"]], ["beta", "gamma", "alpha"])

        first = data["strategies"][0]
        self.assertIn("created_at", first)
        self.assertIn("updated_at", first)
        self.assertIn("size", first)

    def test_list_strategies_q_limit_offset(self):
        self._set_strategy("demo_old", "print('a')\n", 1700000000)
        self._set_strategy("other", "print('b')\n", 1700000050)
        self._set_strategy("demo_new", "print('c')\n", 1700000100)

        resp = self.client.get("/api/backtest/strategies?q=demo&limit=1&offset=1", headers=self._auth_headers())
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        data = payload["data"]
        self.assertEqual(data["total"], 2)
        self.assertEqual(len(data["strategies"]), 1)
        self.assertEqual(data["strategies"][0]["id"], "demo_old")

    def test_list_strategies_legacy_strategy_returns_null_created_at(self):
        strategies_dir = Path(self.base_dir) / "strategies"
        strategies_dir.mkdir(parents=True, exist_ok=True)
        legacy_path = strategies_dir / "legacy.py"
        legacy_path.write_text("print('legacy')\n", encoding="utf-8")
        os.utime(legacy_path, (1700000000, 1700000000))

        resp = self.client.get("/api/backtest/strategies", headers=self._auth_headers())
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        data = payload["data"]
        self.assertEqual(data["total"], 1)
        strategy = data["strategies"][0]
        self.assertEqual(strategy["id"], "legacy")
        self.assertIn("created_at", strategy)
        self.assertIsNone(strategy["created_at"])
        self.assertIn("updated_at", strategy)
        self.assertIn("size", strategy)

    def test_get_and_upsert_strategy_return_contract_shape(self):
        post_resp = self.client.post(
            "/api/backtest/strategies/demo",
            json={"code": "def init(context):\n    pass\n"},
            headers=self._auth_headers(),
        )
        self.assertEqual(post_resp.status_code, 200)
        post_payload = post_resp.get_json()
        self.assertEqual(post_payload["code"], 200)
        self.assertEqual(post_payload["message"], "ok")
        post_data = post_payload["data"]
        self.assertEqual(post_data["id"], "demo")
        self.assertIn("created_at", post_data)
        self.assertIn("updated_at", post_data)
        self.assertIn("size", post_data)

        get_resp = self.client.get("/api/backtest/strategies/demo", headers=self._auth_headers())
        self.assertEqual(get_resp.status_code, 200)
        get_payload = get_resp.get_json()
        self.assertEqual(get_payload["code"], 200)
        self.assertEqual(get_payload["message"], "ok")
        get_data = get_payload["data"]
        self.assertEqual(get_data["id"], "demo")
        self.assertEqual(get_data["code"], "def init(context):\n    pass\n")
        self.assertIn("created_at", get_data)
        self.assertIn("updated_at", get_data)
        self.assertIn("size", get_data)

    def test_delete_strategy_success(self):
        self.client.post(
            "/api/backtest/strategies/demo",
            json={"code": "print('x')\n"},
            headers=self._auth_headers(),
        )

        delete_resp = self.client.delete("/api/backtest/strategies/demo", headers=self._auth_headers())
        self.assertEqual(delete_resp.status_code, 200)
        delete_payload = delete_resp.get_json()
        self.assertEqual(delete_payload["code"], 200)
        self.assertEqual(delete_payload["message"], "deleted")
        self.assertEqual(delete_payload["data"], {"strategy_id": "demo", "deleted": True})

        get_resp = self.client.get("/api/backtest/strategies/demo", headers=self._auth_headers())
        self.assertEqual(get_resp.status_code, 404)

    def test_delete_strategy_not_found_returns_404(self):
        resp = self.client.delete("/api/backtest/strategies/not-exists", headers=self._auth_headers())
        self.assertEqual(resp.status_code, 404)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "NOT_FOUND")

    def test_delete_strategy_referenced_returns_409(self):
        self.client.post(
            "/api/backtest/strategies/demo",
            json={"code": "print('x')\n"},
            headers=self._auth_headers(),
        )
        self._seed_strategy_reference("demo", "job_ref_1")

        resp = self.client.delete("/api/backtest/strategies/demo", headers=self._auth_headers())
        self.assertEqual(resp.status_code, 409)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "CONFLICT")
        self.assertIn("referenced", payload["error"]["message"])
        self.assertEqual(payload["data"]["strategy_id"], "demo")
        self.assertEqual(payload["data"]["job_ids"], ["job_ref_1"])

    def test_delete_strategy_cascade_removes_jobs_and_rename_map(self):
        self.client.post(
            "/api/backtest/strategies/demo",
            json={"code": "print('x')\n"},
            headers=self._auth_headers(),
        )
        rename_resp = self.client.post(
            "/api/backtest/strategies/demo/rename",
            json={"to_id": "alpha"},
            headers=self._auth_headers(),
        )
        self.assertEqual(rename_resp.status_code, 200)

        self._seed_strategy_reference("demo", "job_demo_legacy")
        self._seed_strategy_reference("alpha", "job_alpha_current")

        resp = self.client.delete("/api/backtest/strategies/demo?cascade=true", headers=self._auth_headers())
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["strategy_id"], "alpha")
        self.assertEqual(payload["data"]["deleted_jobs"], 2)

        get_resp = self.client.get("/api/backtest/strategies/alpha", headers=self._auth_headers())
        self.assertEqual(get_resp.status_code, 404)

        map_resp = self.client.get("/api/backtest/strategy-renames", headers=self._auth_headers())
        self.assertEqual(map_resp.status_code, 200)
        self.assertEqual(map_resp.get_json()["data"]["map"], {})

        index_demo = Path(self.base_dir) / "runs_index" / "job_demo_legacy.json"
        index_alpha = Path(self.base_dir) / "runs_index" / "job_alpha_current.json"
        self.assertFalse(index_demo.exists())
        self.assertFalse(index_alpha.exists())

    def test_delete_strategy_cascade_not_found_returns_404(self):
        resp = self.client.delete("/api/backtest/strategies/not-exists?cascade=true", headers=self._auth_headers())
        self.assertEqual(resp.status_code, 404)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "NOT_FOUND")

    def test_list_strategies_invalid_limit_or_offset_returns_400(self):
        cases = [
            "/api/backtest/strategies?limit=0",
            "/api/backtest/strategies?limit=501",
            "/api/backtest/strategies?limit=abc",
            "/api/backtest/strategies?offset=-1",
            "/api/backtest/strategies?offset=abc",
        ]
        for url in cases:
            with self.subTest(url=url):
                resp = self.client.get(url, headers=self._auth_headers())
                self.assertEqual(resp.status_code, 400)
                payload = resp.get_json()
                self.assertIn("error", payload)
                self.assertIsInstance(payload["error"], dict)
                self.assertEqual(payload["error"]["code"], "INVALID_ARGUMENT")

    def test_list_strategies_without_auth_header_returns_401(self):
        resp = self.client.get("/api/backtest/strategies")
        self.assertEqual(resp.status_code, 401)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "UNAUTHORIZED")

    def test_strategy_id_invalid_returns_400(self):
        resp = self.client.post(
            "/api/backtest/strategies/bad$id",
            json={"code": "print('x')"},
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "INVALID_ARGUMENT")
        self.assertTrue(resp.is_json)
        self.assertNotIn("<html", resp.get_data(as_text=True).lower())

    def test_strategy_id_valid_characters_support_cjk_and_mixed_ids(self):
        strategy_ids = ["策略A", "ETF_轮动-2026", "策略123"]
        headers = self._auth_headers()
        for strategy_id in strategy_ids:
            with self.subTest(strategy_id=strategy_id):
                encoded_id = quote(strategy_id, safe="")
                save_resp = self.client.post(
                    f"/api/backtest/strategies/{encoded_id}",
                    json={"code": "def init(context):\n    pass\n"},
                    headers=headers,
                )
                self.assertEqual(save_resp.status_code, 200)
                save_payload = save_resp.get_json()
                self.assertEqual(save_payload["data"]["id"], strategy_id)

                get_resp = self.client.get(
                    f"/api/backtest/strategies/{encoded_id}",
                    headers=headers,
                )
                self.assertEqual(get_resp.status_code, 200)
                self.assertEqual(get_resp.get_json()["data"]["id"], strategy_id)

    def test_legacy_strategy_id_with_dot_remains_accessible(self):
        headers = self._auth_headers()
        strategy_id = "alpha.v1"
        save_resp = self.client.post(
            f"/api/backtest/strategies/{quote(strategy_id, safe='')}",
            json={"code": "def init(context):\n    pass\n"},
            headers=headers,
        )
        self.assertEqual(save_resp.status_code, 200)
        get_resp = self.client.get(
            f"/api/backtest/strategies/{quote(strategy_id, safe='')}",
            headers=headers,
        )
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.get_json()["data"]["id"], strategy_id)

    def test_not_found_route_returns_json_error_body(self):
        resp = self.client.get("/api/backtest/not-found-route", headers=self._auth_headers())
        self.assertEqual(resp.status_code, 404)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "NOT_FOUND")
        self.assertTrue(resp.is_json)
        self.assertNotIn("<html", resp.get_data(as_text=True).lower())

    def test_method_not_allowed_returns_json_error_body(self):
        resp = self.client.post("/api/backtest/jobs/job_foo", headers=self._auth_headers())
        self.assertEqual(resp.status_code, 405)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "METHOD_NOT_ALLOWED")
        self.assertTrue(resp.is_json)
        self.assertNotIn("<html", resp.get_data(as_text=True).lower())

    def test_strategy_path_traversal_attempt_returns_json_error_body(self):
        resp = self.client.get(
            "/api/backtest/strategies/..%2F..%2Fetc%2Fpasswd",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 404)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "NOT_FOUND")
        self.assertTrue(resp.is_json)
        self.assertNotIn("<html", resp.get_data(as_text=True).lower())

    def test_compile_strategy_success_uses_saved_code_when_code_is_empty(self):
        self.client.post(
            "/api/backtest/strategies/demo",
            json={"code": "def init(context):\n    pass\n"},
            headers=self._auth_headers(),
        )

        resp = self.client.post(
            "/api/backtest/strategies/demo/compile",
            json={"code": "   "},
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(set(payload.keys()), {"ok", "stdout", "stderr", "diagnostics"})
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["stderr"], "")
        self.assertEqual(payload["diagnostics"], [])
        self.assertIn("syntax check passed", payload["stdout"])

    def test_compile_strategy_allows_installed_third_party_dependency(self):
        self.client.post(
            "/api/backtest/strategies/demo",
            json={"code": "def init(context):\n    pass\n"},
            headers=self._auth_headers(),
        )

        resp = self.client.post(
            "/api/backtest/strategies/demo/compile",
            json={"code": "import flask\n\ndef init(context):\n    pass\n"},
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["diagnostics"], [])
        self.assertIn("dependency check passed", payload["stdout"])

    def test_compile_strategy_temporary_code_does_not_persist(self):
        original_code = "def init(context):\n    pass\n"
        self.client.post(
            "/api/backtest/strategies/demo",
            json={"code": original_code},
            headers=self._auth_headers(),
        )

        resp = self.client.post(
            "/api/backtest/strategies/demo/compile",
            json={"code": "def init(:\n    pass\n"},
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 422)
        payload = resp.get_json()
        self.assertFalse(payload["ok"])
        self.assertGreaterEqual(len(payload["diagnostics"]), 1)
        self.assertEqual(payload["diagnostics"][0]["line"], 1)
        self.assertGreaterEqual(payload["diagnostics"][0]["column"], 1)

        with self.app.app_context():
            current_code = load_strategy("demo")
        self.assertEqual(current_code, original_code)

    def test_compile_strategy_missing_dependency_returns_422(self):
        self.client.post(
            "/api/backtest/strategies/demo",
            json={"code": "def init(context):\n    pass\n"},
            headers=self._auth_headers(),
        )

        resp = self.client.post(
            "/api/backtest/strategies/demo/compile",
            json={"code": "import package_that_should_not_exist_12345\n"},
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 422)
        payload = resp.get_json()
        self.assertFalse(payload["ok"])
        self.assertEqual(len(payload["diagnostics"]), 1)
        self.assertEqual(payload["diagnostics"][0]["line"], 1)
        self.assertEqual(payload["diagnostics"][0]["column"], 1)
        self.assertEqual(payload["diagnostics"][0]["level"], "error")
        self.assertIn("not installed", payload["diagnostics"][0]["message"])

    def test_compile_strategy_invalid_code_type_returns_400(self):
        resp = self.client.post(
            "/api/backtest/strategies/demo/compile",
            json={"code": 123},
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["stderr"], "code must be a string")
        self.assertEqual(payload["diagnostics"][0]["line"], 0)
        self.assertEqual(payload["diagnostics"][0]["column"], 0)

    def test_compile_strategy_invalid_strategy_id_returns_400(self):
        resp = self.client.post(
            "/api/backtest/strategies/bad$id/compile",
            json={"code": "print('x')\n"},
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertFalse(payload["ok"])
        self.assertIn("strategy_id", payload["stderr"])
        self.assertIn("strategy_id", payload["diagnostics"][0]["message"])

    def test_compile_strategy_non_admin_returns_403(self):
        resp = self.client.post(
            "/api/backtest/strategies/demo/compile",
            json={"code": "print('x')\n"},
            headers=self._auth_headers(is_admin=False),
        )
        self.assertEqual(resp.status_code, 403)
        payload = resp.get_json()
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["stderr"], "admin role required")

    def test_compile_strategy_internal_error_returns_500(self):
        self.client.post(
            "/api/backtest/strategies/demo",
            json={"code": "def init(context):\n    pass\n"},
            headers=self._auth_headers(),
        )
        fake_result = {
            "ok": False,
            "stdout": "",
            "stderr": "compile timeout after 10s",
            "diagnostics": [{"line": 0, "column": 0, "level": "error", "message": "compile timeout after 10s"}],
        }
        with patch("app.api.backtest_api.compile_strategy_debug", return_value=(fake_result, "internal_error")):
            resp = self.client.post(
                "/api/backtest/strategies/demo/compile",
                json={},
                headers=self._auth_headers(),
            )
        self.assertEqual(resp.status_code, 500)
        payload = resp.get_json()
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["stderr"], "compile timeout after 10s")

    def test_compile_strategy_missing_saved_code_returns_400(self):
        resp = self.client.post(
            "/api/backtest/strategies/not_found/compile",
            json={},
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["stderr"], "strategy code not found")

    def test_strategy_rename_success_writes_map_and_supports_alias_read(self):
        self.client.post(
            "/api/backtest/strategies/demo",
            json={"code": "print('demo')\n"},
            headers=self._auth_headers(),
        )

        rename_resp = self.client.post(
            "/api/backtest/strategies/demo/rename",
            json={"to_id": "alpha"},
            headers=self._auth_headers(),
        )
        self.assertEqual(rename_resp.status_code, 200)
        rename_payload = rename_resp.get_json()
        self.assertTrue(rename_payload["ok"])
        self.assertEqual(rename_payload["data"]["from_id"], "demo")
        self.assertEqual(rename_payload["data"]["to_id"], "alpha")
        self.assertTrue(rename_payload["data"]["deleted_old"])

        map_resp = self.client.get("/api/backtest/strategy-renames", headers=self._auth_headers())
        self.assertEqual(map_resp.status_code, 200)
        mapping = map_resp.get_json()["data"]["map"]
        self.assertEqual(mapping.get("demo"), "alpha")

        alias_get_resp = self.client.get("/api/backtest/strategies/demo", headers=self._auth_headers())
        self.assertEqual(alias_get_resp.status_code, 200)
        self.assertEqual(alias_get_resp.get_json()["data"]["id"], "alpha")

    def test_strategy_rename_supports_url_encoded_cjk_ids(self):
        headers = self._auth_headers()
        from_id = "策略A"
        to_id = "ETF_轮动-2026"

        create_resp = self.client.post(
            f"/api/backtest/strategies/{quote(from_id, safe='')}",
            json={"code": "print('demo')\n"},
            headers=headers,
        )
        self.assertEqual(create_resp.status_code, 200)

        rename_resp = self.client.post(
            f"/api/backtest/strategies/{quote(from_id, safe='')}/rename",
            json={"to_id": to_id},
            headers=headers,
        )
        self.assertEqual(rename_resp.status_code, 200)
        rename_payload = rename_resp.get_json()["data"]
        self.assertEqual(rename_payload["from_id"], from_id)
        self.assertEqual(rename_payload["to_id"], to_id)

        map_resp = self.client.get("/api/backtest/strategy-renames", headers=headers)
        self.assertEqual(map_resp.status_code, 200)
        self.assertEqual(map_resp.get_json()["data"]["map"].get(from_id), to_id)

    def test_strategy_rename_invalid_ids_return_field_specific_422(self):
        headers = self._auth_headers()
        self.client.post(
            f"/api/backtest/strategies/{quote('策略A', safe='')}",
            json={"code": "print('demo')\n"},
            headers=headers,
        )

        cases = [
            ("策略 A", "策略B", "from_id contains invalid characters"),
            ("策略A", "ETF 轮动-2026", "to_id contains invalid characters"),
            ("策略A", "策略/一", "to_id contains invalid characters"),
            ("策略A", "策略@1", "to_id contains invalid characters"),
        ]
        for from_id, to_id, expected_message in cases:
            with self.subTest(from_id=from_id, to_id=to_id):
                resp = self.client.post(
                    f"/api/backtest/strategies/{quote(from_id, safe='')}/rename",
                    json={"to_id": to_id},
                    headers=headers,
                )
                self.assertEqual(resp.status_code, 422)
                payload = resp.get_json()
                self.assertEqual(payload["error"]["code"], "UNPROCESSABLE_ENTITY")
                self.assertEqual(payload["error"]["message"], expected_message)

    def test_strategy_rename_mapping_upsert_uses_same_strategy_id_validation(self):
        headers = self._auth_headers()
        ok_resp = self.client.post(
            "/api/backtest/strategy-renames",
            json={"from_id": "策略A", "to_id": "策略123"},
            headers=headers,
        )
        self.assertEqual(ok_resp.status_code, 200)

        cases = [
            ({"from_id": "策略 A", "to_id": "策略123"}, "from_id contains invalid characters"),
            ({"from_id": "策略A", "to_id": "策略 123"}, "to_id contains invalid characters"),
            ({"from_id": "策略A", "to_id": "策略/123"}, "to_id contains invalid characters"),
        ]
        for body, expected_message in cases:
            with self.subTest(body=body):
                resp = self.client.post(
                    "/api/backtest/strategy-renames",
                    json=body,
                    headers=headers,
                )
                self.assertEqual(resp.status_code, 422)
                payload = resp.get_json()
                self.assertEqual(payload["error"]["code"], "UNPROCESSABLE_ENTITY")
                self.assertEqual(payload["error"]["message"], expected_message)

    def test_invalid_rename_map_rows_do_not_break_strategy_access(self):
        headers = self._auth_headers()
        self.client.post(
            "/api/backtest/strategies/demo",
            json={"code": "print('demo')\n"},
            headers=headers,
        )

        db_path = Path(self.base_dir) / "backtest_meta.sqlite3"
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS backtest_strategy_rename_map (
                    from_id TEXT PRIMARY KEY,
                    to_id TEXT NOT NULL,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT NULL,
                    CHECK (from_id <> to_id)
                )
                """
            )
            conn.execute(
                """
                INSERT OR REPLACE INTO backtest_strategy_rename_map (from_id, to_id, updated_by)
                VALUES (?, ?, ?)
                """,
                ("bad id", "demo", "test"),
            )

        get_resp = self.client.get("/api/backtest/strategies/demo", headers=headers)
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.get_json()["data"]["id"], "demo")

    def test_strategy_rename_chain_is_compressed(self):
        self.client.post(
            "/api/backtest/strategies/demo",
            json={"code": "print('demo')\n"},
            headers=self._auth_headers(),
        )
        self.client.post(
            "/api/backtest/strategies/demo/rename",
            json={"to_id": "alpha"},
            headers=self._auth_headers(),
        )
        second = self.client.post(
            "/api/backtest/strategies/alpha/rename",
            json={"to_id": "beta"},
            headers=self._auth_headers(),
        )
        self.assertEqual(second.status_code, 200)

        map_resp = self.client.get("/api/backtest/strategy-renames", headers=self._auth_headers())
        mapping = map_resp.get_json()["data"]["map"]
        self.assertEqual(mapping.get("demo"), "beta")
        self.assertEqual(mapping.get("alpha"), "beta")
        self.assertNotEqual(mapping.get("demo"), "alpha")

    def test_strategy_rename_repeat_request_is_idempotent(self):
        self.client.post(
            "/api/backtest/strategies/alpha",
            json={"code": "print('alpha')\n"},
            headers=self._auth_headers(),
        )
        first = self.client.post(
            "/api/backtest/strategies/alpha/rename",
            json={"to_id": "beta"},
            headers=self._auth_headers(),
        )
        second = self.client.post(
            "/api/backtest/strategies/alpha/rename",
            json={"to_id": "beta"},
            headers=self._auth_headers(),
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        second_payload = second.get_json()
        self.assertTrue(second_payload["ok"])
        self.assertIn("noop", second_payload["data"]["warning"])

        map_resp = self.client.get("/api/backtest/strategy-renames", headers=self._auth_headers())
        mapping = map_resp.get_json()["data"]["map"]
        self.assertEqual(mapping.get("alpha"), "beta")

    def test_strategy_rename_concurrent_writes_do_not_create_cycle_or_dirty_map(self):
        headers = self._auth_headers()

        def _post_mapping(from_id: str, to_id: str) -> int:
            with self.app.test_client() as client:
                response = client.post(
                    "/api/backtest/strategy-renames",
                    json={"from_id": from_id, "to_id": to_id},
                    headers=headers,
                )
                return response.status_code

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(_post_mapping, "legacy_demo", "alpha"),
                executor.submit(_post_mapping, "alpha", "beta"),
            ]
            statuses = [future.result(timeout=5) for future in futures]
        self.assertTrue(all(status == 200 for status in statuses))

        map_resp = self.client.get("/api/backtest/strategy-renames", headers=headers)
        self.assertEqual(map_resp.status_code, 200)
        mapping = map_resp.get_json()["data"]["map"]
        self.assertEqual(mapping.get("legacy_demo"), "beta")
        self.assertEqual(mapping.get("alpha"), "beta")
        self.assertNotIn("beta", mapping)

    def test_strategy_rename_same_id_returns_noop_success(self):
        self.client.post(
            "/api/backtest/strategies/demo",
            json={"code": "print('demo')\n"},
            headers=self._auth_headers(),
        )
        resp = self.client.post(
            "/api/backtest/strategies/demo/rename",
            json={"to_id": "demo"},
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["data"]["deleted_old"])
        self.assertIn("noop", payload["data"]["warning"])


if __name__ == "__main__":
    unittest.main()
