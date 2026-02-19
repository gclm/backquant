import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import jwt
from flask import Flask

from app.api.backtest_api import bp_backtest
from app.backtest.services.runner import (
    save_strategy,
    update_job_index,
    write_job_index,
    write_job_meta,
    write_status,
)


class BacktestJobsApiTestCase(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self._tmpdir.name)

        app = Flask(__name__)
        app.config.update(
            BACKTEST_BASE_DIR=str(self.base_dir),
            RQALPHA_BUNDLE_PATH="/tmp",
            BACKTEST_TIMEOUT=1,
            BACKTEST_KEEP_DAYS=30,
            BACKTEST_IDEMPOTENCY_WINDOW_SECONDS=60,
            SECRET_KEY="test-secret",
            TESTING=True,
        )
        app.register_blueprint(bp_backtest)
        self.app = app
        self.client = app.test_client()

    def tearDown(self):
        self._tmpdir.cleanup()

    def _auth_headers(self) -> dict:
        token = jwt.encode(
            {
                "user_id": 1,
                "is_admin": True,
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            },
            self.app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return {"Authorization": token}

    def _create_job_dir(self, job_id: str) -> Path:
        job_dir = self.base_dir / "runs" / "2026-02-16" / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        with self.app.app_context():
            write_job_index(job_id, job_dir)
        return job_dir

    def _save_strategy(self, strategy_id: str, code: str) -> None:
        with self.app.app_context():
            save_strategy(strategy_id, code)

    def _seed_strategy_job(
        self,
        *,
        job_id: str,
        strategy_id: str,
        status: str,
        created_at: str,
        updated_at: str,
        error: dict | None = None,
    ) -> Path:
        job_dir = self._create_job_dir(job_id)
        write_status(
            job_dir,
            status,
            error.get("code") if error else None,
            error.get("message") if error else None,
        )
        with self.app.app_context():
            write_job_meta(
                job_dir,
                strategy_id=strategy_id,
                start_date="2020-01-01",
                end_date="2020-12-31",
                cash=100000,
                benchmark="000300.XSHG",
                frequency="1d",
                code_sha256=f"{strategy_id}-{job_id}",
            )
            update_job_index(
                job_id,
                strategy_id=strategy_id,
                status=status,
                created_at=created_at,
                updated_at=updated_at,
                params={
                    "start_date": "2020-01-01",
                    "end_date": "2020-12-31",
                    "cash": 100000,
                    "benchmark": "000300.XSHG",
                    "frequency": "1d",
                },
                error=error,
            )
        return job_dir

    @staticmethod
    def _valid_run_body(strategy_id: str = "demo") -> dict:
        return {
            "strategy_id": strategy_id,
            "start_date": "2020-01-01",
            "end_date": "2020-12-31",
            "cash": 100000,
            "benchmark": "000300.XSHG",
            "frequency": "1d",
        }

    def test_backtest_routes_require_auth(self):
        resp = self.client.get("/api/backtest/strategies")
        self.assertEqual(resp.status_code, 401)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "UNAUTHORIZED")

    def test_job_status_returns_structured_error(self):
        job_dir = self._create_job_dir("job_status_err")
        write_status(job_dir, "FAILED", "RQALPHA_TIMEOUT", "rqalpha timeout")

        resp = self.client.get("/api/backtest/jobs/job_status_err", headers=self._auth_headers())
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload["status"], "FAILED")
        self.assertEqual(payload["error"]["code"], "RQALPHA_TIMEOUT")
        self.assertEqual(payload["error"]["message"], "rqalpha timeout")
        self.assertEqual(payload["error_message"], "rqalpha timeout")

    def test_job_result_not_ready_returns_409(self):
        job_dir = self._create_job_dir("job_not_ready")
        write_status(job_dir, "RUNNING")

        resp = self.client.get(
            "/api/backtest/jobs/job_not_ready/result",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 409)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "RESULT_NOT_READY")
        self.assertEqual(payload["status"], "RUNNING")

    def test_job_result_returns_normalized_empty_structure(self):
        job_dir = self._create_job_dir("job_empty_result")
        write_status(job_dir, "FINISHED")
        (job_dir / "extracted.json").write_text("{}", encoding="utf-8")

        resp = self.client.get(
            "/api/backtest/jobs/job_empty_result/result",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload["summary"], {})
        self.assertEqual(
            payload["equity"],
            {"dates": [], "nav": [], "returns": [], "benchmark_nav": []},
        )
        self.assertEqual(payload["trades"], [])
        self.assertEqual(payload["trade_columns"], [])
        self.assertEqual(payload["trades_total"], 0)
        self.assertIsInstance(payload["raw_keys"], list)

    def test_job_result_trades_pagination(self):
        job_dir = self._create_job_dir("job_result_page")
        write_status(job_dir, "FINISHED")
        payload = {
            "summary": {"a": 1},
            "equity": {"dates": ["2026-01-01"], "nav": [1.0], "returns": [0.0]},
            "trades": [{"id": 1}, {"id": 2}, {"id": 3}],
            "raw_keys": ["summary", "equity", "trades"],
        }
        (job_dir / "extracted.json").write_text(json.dumps(payload), encoding="utf-8")

        resp = self.client.get(
            "/api/backtest/jobs/job_result_page/result?page=2&page_size=2",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["trades_total"], 3)
        self.assertEqual(data["page"], 2)
        self.assertEqual(data["page_size"], 2)
        self.assertEqual(data["trades"], [{"id": 3}])
        self.assertEqual(data["trade_columns"], ["id"])
        self.assertEqual(data["equity"]["benchmark_nav"], [])

    def test_job_result_exposes_equity_benchmark_nav(self):
        job_dir = self._create_job_dir("job_result_benchmark_nav")
        write_status(job_dir, "FINISHED")
        payload = {
            "summary": {"a": 1},
            "equity": {
                "dates": ["2026-01-01", "2026-01-02"],
                "nav": [1.0, 1.01],
                "returns": [0.0, 0.01],
                "benchmark_nav": [1.0, 1.005],
            },
            "trades": [],
            "raw_keys": ["summary", "equity", "trades"],
        }
        (job_dir / "extracted.json").write_text(json.dumps(payload), encoding="utf-8")

        resp = self.client.get(
            "/api/backtest/jobs/job_result_benchmark_nav/result",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["equity"]["dates"], ["2026-01-01", "2026-01-02"])
        self.assertEqual(data["equity"]["nav"], [1.0, 1.01])
        self.assertEqual(data["equity"]["benchmark_nav"], [1.0, 1.005])

    def test_job_result_legacy_benchmark_curve_fallback(self):
        job_dir = self._create_job_dir("job_result_legacy_benchmark")
        write_status(job_dir, "FINISHED")
        payload = {
            "summary": {"benchmark_total_returns": 0.1},
            "equity": {"dates": ["2026-01-01"], "nav": [1.0], "returns": [0.0]},
            "benchmark_curve": [1.0],
            "trades": [],
            "raw_keys": ["summary", "equity", "benchmark_curve", "trades"],
        }
        (job_dir / "extracted.json").write_text(json.dumps(payload), encoding="utf-8")

        resp = self.client.get(
            "/api/backtest/jobs/job_result_legacy_benchmark/result",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["equity"]["benchmark_nav"], [1.0])

    def test_job_log_incremental_offset_and_tail(self):
        job_dir = self._create_job_dir("job_log_inc")
        (job_dir / "run.log").write_text("line1\nline2\nline3\n", encoding="utf-8")

        resp_offset = self.client.get(
            "/api/backtest/jobs/job_log_inc/log?offset=6",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp_offset.status_code, 200)
        payload_offset = resp_offset.get_json()
        self.assertEqual(payload_offset["content"], "line2\nline3\n")
        self.assertEqual(payload_offset["offset"], 6)
        self.assertEqual(payload_offset["next_offset"], len("line1\nline2\nline3\n"))

        resp_tail = self.client.get(
            "/api/backtest/jobs/job_log_inc/log?tail=6",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp_tail.status_code, 200)
        payload_tail = resp_tail.get_json()
        self.assertEqual(payload_tail["content"], "line3\n")

    def test_job_log_invalid_query_returns_400(self):
        job_dir = self._create_job_dir("job_log_bad")
        (job_dir / "run.log").write_text("line\n", encoding="utf-8")

        cases = [
            "/api/backtest/jobs/job_log_bad/log?offset=-1",
            "/api/backtest/jobs/job_log_bad/log?tail=0",
            "/api/backtest/jobs/job_log_bad/log?offset=1&tail=2",
        ]
        for url in cases:
            with self.subTest(url=url):
                resp = self.client.get(url, headers=self._auth_headers())
                self.assertEqual(resp.status_code, 400)
                payload = resp.get_json()
                self.assertEqual(payload["error"]["code"], "INVALID_ARGUMENT")

    def test_run_idempotency_reuses_job_id_within_window(self):
        self._save_strategy("demo", "def init(context):\n    pass\n")
        body = self._valid_run_body("demo")
        with patch("app.api.backtest_api.threading.Thread") as thread_cls:
            thread_instance = Mock()
            thread_cls.return_value = thread_instance

            first = self.client.post("/api/backtest/run", json=body, headers=self._auth_headers())
            second = self.client.post("/api/backtest/run", json=body, headers=self._auth_headers())

            self.assertEqual(first.status_code, 200)
            self.assertEqual(second.status_code, 200)
            first_job_id = first.get_json()["job_id"]
            second_job_id = second.get_json()["job_id"]
            self.assertEqual(first_job_id, second_job_id)
            self.assertEqual(thread_cls.call_count, 1)
            self.assertEqual(thread_instance.start.call_count, 1)

    def test_run_accepts_cjk_and_mixed_strategy_id(self):
        strategy_id = "ETF_轮动-2026"
        self._save_strategy(strategy_id, "def init(context):\n    pass\n")
        body = self._valid_run_body(strategy_id)
        with patch("app.api.backtest_api.threading.Thread") as thread_cls:
            thread_instance = Mock()
            thread_cls.return_value = thread_instance
            resp = self.client.post("/api/backtest/run", json=body, headers=self._auth_headers())
        self.assertEqual(resp.status_code, 200)
        self.assertIn("job_id", resp.get_json())
        self.assertEqual(thread_cls.call_count, 1)
        self.assertEqual(thread_instance.start.call_count, 1)

    def test_run_accepts_legacy_strategy_id_with_dot(self):
        strategy_id = "alpha.v1"
        self._save_strategy(strategy_id, "def init(context):\n    pass\n")
        body = self._valid_run_body(strategy_id)
        with patch("app.api.backtest_api.threading.Thread") as thread_cls:
            thread_instance = Mock()
            thread_cls.return_value = thread_instance
            resp = self.client.post("/api/backtest/run", json=body, headers=self._auth_headers())
        self.assertEqual(resp.status_code, 200)
        self.assertIn("job_id", resp.get_json())

    def test_run_rejects_strategy_id_with_invalid_characters(self):
        invalid_ids = ["策略 A", "策略/一", "策略@1"]
        for strategy_id in invalid_ids:
            with self.subTest(strategy_id=strategy_id):
                body = self._valid_run_body(strategy_id)
                resp = self.client.post("/api/backtest/run", json=body, headers=self._auth_headers())
                self.assertEqual(resp.status_code, 400)
                payload = resp.get_json()
                self.assertEqual(payload["error"]["code"], "INVALID_ARGUMENT")
                self.assertEqual(payload["error"]["message"], "strategy_id contains invalid characters")

    def test_run_rejects_invalid_frequency(self):
        self._save_strategy("demo", "def init(context):\n    pass\n")
        body = self._valid_run_body("demo")
        body["frequency"] = "2d"

        resp = self.client.post("/api/backtest/run", json=body, headers=self._auth_headers())
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "INVALID_ARGUMENT")
        self.assertIn("frequency", payload["error"]["message"])

    def test_run_rejects_end_date_earlier_than_start_date(self):
        self._save_strategy("demo", "def init(context):\n    pass\n")
        body = self._valid_run_body("demo")
        body["start_date"] = "2020-12-31"
        body["end_date"] = "2020-01-01"

        resp = self.client.post("/api/backtest/run", json=body, headers=self._auth_headers())
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "INVALID_ARGUMENT")
        self.assertIn("end_date must be >=", payload["error"]["message"])

    def test_run_rejects_non_positive_cash(self):
        self._save_strategy("demo", "def init(context):\n    pass\n")
        body = self._valid_run_body("demo")
        body["cash"] = 0

        resp = self.client.post("/api/backtest/run", json=body, headers=self._auth_headers())
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "INVALID_ARGUMENT")
        self.assertEqual(payload["error"]["message"], "cash must be > 0")

    def test_run_returns_404_for_missing_strategy(self):
        body = self._valid_run_body("no_such_strategy")

        resp = self.client.post("/api/backtest/run", json=body, headers=self._auth_headers())
        self.assertEqual(resp.status_code, 404)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "NOT_FOUND")
        self.assertEqual(payload["error"]["message"], "strategy not found")

    def test_strategy_jobs_list_returns_only_target_strategy_with_pagination(self):
        self._seed_strategy_job(
            job_id="job_alpha_old",
            strategy_id="alpha",
            status="FINISHED",
            created_at="2026-02-14T09:00:00+08:00",
            updated_at="2026-02-14T10:00:00+08:00",
        )
        self._seed_strategy_job(
            job_id="job_beta",
            strategy_id="beta",
            status="FAILED",
            created_at="2026-02-15T09:00:00+08:00",
            updated_at="2026-02-15T10:00:00+08:00",
            error={"code": "RQALPHA_EXIT_NONZERO", "message": "rqalpha exit code=1; see run.log"},
        )
        self._seed_strategy_job(
            job_id="job_alpha_new",
            strategy_id="alpha",
            status="RUNNING",
            created_at="2026-02-16T09:00:00+08:00",
            updated_at="2026-02-16T10:00:00+08:00",
        )

        resp_page_1 = self.client.get(
            "/api/backtest/strategies/alpha/jobs?limit=1&offset=0",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp_page_1.status_code, 200)
        payload_page_1 = resp_page_1.get_json()["data"]
        self.assertEqual(payload_page_1["strategy_id"], "alpha")
        self.assertEqual(payload_page_1["total"], 2)
        self.assertEqual([item["job_id"] for item in payload_page_1["jobs"]], ["job_alpha_new"])
        self.assertEqual(payload_page_1["jobs"][0]["status"], "RUNNING")
        self.assertEqual(payload_page_1["jobs"][0]["params"]["benchmark"], "000300.XSHG")

        resp_page_2 = self.client.get(
            "/api/backtest/strategies/alpha/jobs?limit=1&offset=1",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp_page_2.status_code, 200)
        payload_page_2 = resp_page_2.get_json()["data"]
        self.assertEqual([item["job_id"] for item in payload_page_2["jobs"]], ["job_alpha_old"])
        self.assertEqual(payload_page_2["jobs"][0]["status"], "FINISHED")

    def test_strategy_jobs_list_supports_status_filter(self):
        self._seed_strategy_job(
            job_id="job_alpha_ok",
            strategy_id="alpha",
            status="FINISHED",
            created_at="2026-02-16T08:00:00+08:00",
            updated_at="2026-02-16T08:10:00+08:00",
        )
        self._seed_strategy_job(
            job_id="job_alpha_failed",
            strategy_id="alpha",
            status="FAILED",
            created_at="2026-02-16T09:00:00+08:00",
            updated_at="2026-02-16T09:10:00+08:00",
            error={"code": "RQALPHA_TIMEOUT", "message": "rqalpha timeout"},
        )

        resp = self.client.get(
            "/api/backtest/strategies/alpha/jobs?status=FAILED",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()["data"]
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["jobs"][0]["job_id"], "job_alpha_failed")
        self.assertEqual(payload["jobs"][0]["error"]["code"], "RQALPHA_TIMEOUT")

    def test_strategy_jobs_list_exposes_legacy_top_level_fields(self):
        self._seed_strategy_job(
            job_id="job_alpha_legacy",
            strategy_id="alpha",
            status="FINISHED",
            created_at="2026-02-16T08:00:00+08:00",
            updated_at="2026-02-16T08:10:00+08:00",
        )

        resp = self.client.get(
            "/api/backtest/strategies/alpha/jobs?limit=10&offset=0",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)

        payload = resp.get_json()
        self.assertIn("data", payload)
        self.assertEqual(payload["strategy_id"], payload["data"]["strategy_id"])
        self.assertEqual(payload["total"], payload["data"]["total"])
        self.assertEqual(payload["jobs"], payload["data"]["jobs"])
        self.assertEqual(payload["jobs"][0]["job_id"], "job_alpha_legacy")

    def test_strategy_jobs_list_falls_back_to_job_meta_when_index_missing_strategy_id(self):
        job_dir = self._create_job_dir("job_meta_only")
        write_status(job_dir, "FINISHED")
        with self.app.app_context():
            write_job_meta(
                job_dir,
                strategy_id="meta_demo",
                start_date="2021-01-01",
                end_date="2021-12-31",
                cash=200000,
                benchmark="000905.XSHG",
                frequency="1d",
                code_sha256="abc123",
            )
            update_job_index(
                "job_meta_only",
                status="FINISHED",
                created_at="2026-02-16T10:00:00+08:00",
                updated_at="2026-02-16T10:10:00+08:00",
                error=None,
            )

        resp = self.client.get(
            "/api/backtest/strategies/meta_demo/jobs",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()["data"]
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["jobs"][0]["job_id"], "job_meta_only")
        self.assertEqual(payload["jobs"][0]["params"]["benchmark"], "000905.XSHG")

    def test_strategy_jobs_list_invalid_status_returns_400(self):
        resp = self.client.get(
            "/api/backtest/strategies/alpha/jobs?status=UNKNOWN",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "INVALID_ARGUMENT")
        self.assertIn("status must be one of", payload["error"]["message"])

    def test_strategy_jobs_list_merges_legacy_alias_ids_after_rename_mapping(self):
        self._seed_strategy_job(
            job_id="job_demo_legacy",
            strategy_id="demo",
            status="FINISHED",
            created_at="2026-02-16T08:00:00+08:00",
            updated_at="2026-02-16T08:10:00+08:00",
        )
        self._seed_strategy_job(
            job_id="job_alpha_current",
            strategy_id="alpha",
            status="RUNNING",
            created_at="2026-02-16T09:00:00+08:00",
            updated_at="2026-02-16T09:10:00+08:00",
        )

        map_resp = self.client.post(
            "/api/backtest/strategy-renames",
            json={"from_id": "demo", "to_id": "alpha"},
            headers=self._auth_headers(),
        )
        self.assertEqual(map_resp.status_code, 200)

        resp = self.client.get(
            "/api/backtest/strategies/alpha/jobs",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()["data"]
        self.assertEqual(payload["strategy_id"], "alpha")
        self.assertEqual(payload["total"], 2)
        self.assertEqual({item["job_id"] for item in payload["jobs"]}, {"job_demo_legacy", "job_alpha_current"})
        self.assertTrue(all(item["strategy_id"] == "alpha" for item in payload["jobs"]))

    def test_strategy_jobs_list_limit_gt_1000_returns_400(self):
        resp = self.client.get(
            "/api/backtest/strategies/alpha/jobs?limit=1001",
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertEqual(payload["error"]["code"], "INVALID_ARGUMENT")
        self.assertIn("limit must be <= 1000", payload["error"]["message"])

    def test_delete_job_success_and_repeat_returns_404(self):
        job_dir = self._create_job_dir("job_delete_demo")
        write_status(job_dir, "FAILED", "RQALPHA_TIMEOUT", "rqalpha timeout")

        first = self.client.delete(
            "/api/backtest/jobs/job_delete_demo",
            headers=self._auth_headers(),
        )
        self.assertEqual(first.status_code, 200)
        first_payload = first.get_json()
        self.assertTrue(first_payload["ok"])
        self.assertEqual(first_payload["data"]["job_id"], "job_delete_demo")
        self.assertEqual(first_payload["data"]["deleted"], True)

        second = self.client.delete(
            "/api/backtest/jobs/job_delete_demo",
            headers=self._auth_headers(),
        )
        self.assertEqual(second.status_code, 404)
        second_payload = second.get_json()
        self.assertEqual(second_payload["error"]["code"], "NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
