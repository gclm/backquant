import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from flask import Flask

from app.api.research_api import bp_research
from app.auth import generate_auth_token


class ResearchApiTestCase(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.base_dir = self._tmpdir.name

        app = Flask(__name__)
        app.config.update(
            BACKTEST_BASE_DIR=self.base_dir,
            SECRET_KEY="test-secret",
            TESTING=True,
            RESEARCH_SESSION_TTL_SECONDS=3600,
            RESEARCH_NOTEBOOK_PROXY_BASE="/jupyter",
            RESEARCH_NOTEBOOK_ROOT_DIR=str(Path(self.base_dir) / "research/notebooks"),
        )
        app.register_blueprint(bp_research)
        self.app = app
        self.client = app.test_client()

    def tearDown(self):
        self._tmpdir.cleanup()

    def _auth_headers(self) -> dict:
        with self.app.app_context():
            token = generate_auth_token(user_id=1, is_admin=True)
        return {"Authorization": token}

    def _create_item(
        self,
        research_id: str = "factor_rotation_v1",
        notebook_path: str | None = "research/notebooks/workbench.ipynb",
    ):
        payload = {
            "id": research_id,
            "title": "因子轮动研究",
            "description": "demo",
            "kernel": "python3",
            "status": "ACTIVE",
            "tags": ["alpha", "rqalpha"],
        }
        if notebook_path is not None:
            payload["notebook_path"] = notebook_path
        resp = self.client.post(
            "/api/research/items",
            json=payload,
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 201)
        return resp.get_json()["research"]

    def test_items_crud(self):
        created = self._create_item()
        self.assertEqual(created["id"], "factor_rotation_v1")
        self.assertEqual(created["notebook_path"], "factor_rotation_v1.ipynb")
        self.assertIn("created_at", created)
        self.assertIn("updated_at", created)

        list_resp = self.client.get("/api/research/items", headers=self._auth_headers())
        self.assertEqual(list_resp.status_code, 200)
        items = list_resp.get_json()["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], "factor_rotation_v1")
        self.assertIn("session_status", items[0])
        self.assertIsNone(items[0]["session_status"])

        get_resp = self.client.get("/api/research/items/factor_rotation_v1", headers=self._auth_headers())
        self.assertEqual(get_resp.status_code, 200)
        get_payload = get_resp.get_json()["research"]
        self.assertEqual(get_payload["title"], "因子轮动研究")

        put_resp = self.client.put(
            "/api/research/items/factor_rotation_v1",
            json={
                "id": "factor_rotation_v1",
                "title": "因子轮动研究-更新",
                "description": "demo2",
                "kernel": "python3",
                "status": "DRAFT",
                "tags": ["alpha"],
            },
            headers=self._auth_headers(),
        )
        self.assertEqual(put_resp.status_code, 200)
        updated = put_resp.get_json()["research"]
        self.assertEqual(updated["title"], "因子轮动研究-更新")
        self.assertEqual(updated["status"], "DRAFT")
        self.assertEqual(updated["notebook_path"], "factor_rotation_v1.ipynb")

        delete_resp = self.client.delete(
            "/api/research/items/factor_rotation_v1",
            headers=self._auth_headers(),
        )
        self.assertEqual(delete_resp.status_code, 200)
        self.assertEqual(delete_resp.get_json(), {"ok": True, "id": "factor_rotation_v1"})

    def test_session_lifecycle(self):
        self._create_item("alpha_workbench")

        not_found_resp = self.client.get(
            "/api/research/items/alpha_workbench/notebook/session",
            headers=self._auth_headers(),
        )
        self.assertEqual(not_found_resp.status_code, 404)
        self.assertEqual(not_found_resp.get_json()["message"], "session not found")

        create_resp = self.client.post(
            "/api/research/items/alpha_workbench/notebook/session",
            json={"notebook_path": "research/notebooks/workbench.ipynb", "kernel": "python3"},
            headers=self._auth_headers(),
        )
        self.assertEqual(create_resp.status_code, 200)
        session = create_resp.get_json()["session"]
        self.assertTrue(session["session_id"].startswith("sess_"))
        self.assertIn("/jupyter/lab/tree/alpha_workbench.ipynb?token=", session["notebook_url"])
        self.assertEqual(session["embed_url"], session["notebook_url"])
        self.assertEqual(session["status"], "RUNNING")
        notebook_file = Path(self.base_dir) / "research/notebooks/alpha_workbench.ipynb"
        self.assertTrue(notebook_file.exists())
        self.assertTrue(notebook_file.is_file())

        get_resp = self.client.get(
            "/api/research/items/alpha_workbench/notebook/session",
            headers=self._auth_headers(),
        )
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.get_json()["session"]["session_id"], session["session_id"])

        refresh_resp = self.client.post(
            "/api/research/items/alpha_workbench/notebook/session/refresh",
            json={"session_id": session["session_id"]},
            headers=self._auth_headers(),
        )
        self.assertEqual(refresh_resp.status_code, 200)
        refreshed = refresh_resp.get_json()["session"]
        self.assertEqual(refreshed["session_id"], session["session_id"])

        delete_resp = self.client.delete(
            f"/api/research/items/alpha_workbench/notebook/session?session_id={session['session_id']}",
            headers=self._auth_headers(),
        )
        self.assertEqual(delete_resp.status_code, 200)
        self.assertEqual(delete_resp.get_json(), {"ok": True, "session_id": session["session_id"]})

    def test_session_create_is_idempotent_for_same_params(self):
        self._create_item("idem_demo")

        def _create_once():
            with self.app.test_client() as client:
                resp = client.post(
                    "/api/research/items/idem_demo/notebook/session",
                    json={"notebook_path": "research/notebooks/workbench.ipynb", "kernel": "python3"},
                    headers=self._auth_headers(),
                )
                self.assertEqual(resp.status_code, 200)
                return resp.get_json()["session"]["session_id"]

        with ThreadPoolExecutor(max_workers=2) as executor:
            ids = [future.result(timeout=5) for future in [executor.submit(_create_once), executor.submit(_create_once)]]

        self.assertEqual(ids[0], ids[1])

    def test_error_shape_is_message_only(self):
        resp = self.client.post(
            "/api/research/items",
            json={"id": "bad one"},
            headers=self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertEqual(set(payload.keys()), {"message"})

    def test_reject_non_ipynb_notebook_path(self):
        item_resp = self.client.post(
            "/api/research/items",
            json={
                "id": "bad_ext",
                "title": "bad",
                "description": "bad",
                "notebook_path": "research/notebooks/workbench.txt",
                "kernel": "python3",
                "status": "ACTIVE",
                "tags": [],
            },
            headers=self._auth_headers(),
        )
        self.assertEqual(item_resp.status_code, 400)
        self.assertEqual(item_resp.get_json()["message"], "notebook_path must end with .ipynb")

    def test_get_session_backfills_missing_urls(self):
        self._create_item("backfill_demo")
        create_resp = self.client.post(
            "/api/research/items/backfill_demo/notebook/session",
            json={"notebook_path": "research/notebooks/workbench.ipynb", "kernel": "python3"},
            headers=self._auth_headers(),
        )
        self.assertEqual(create_resp.status_code, 200)

        sessions_file = Path(self.base_dir) / "research/sessions.json"
        payload = json.loads(sessions_file.read_text(encoding="utf-8"))
        payload["backfill_demo"]["notebook_url"] = ""
        payload["backfill_demo"]["embed_url"] = ""
        payload["backfill_demo"]["session_token"] = ""
        sessions_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        get_resp = self.client.get(
            "/api/research/items/backfill_demo/notebook/session",
            headers=self._auth_headers(),
        )
        self.assertEqual(get_resp.status_code, 200)
        session = get_resp.get_json()["session"]
        self.assertIn("/jupyter/lab/tree/backfill_demo.ipynb?token=", session["notebook_url"])
        self.assertEqual(session["embed_url"], session["notebook_url"])

    def test_unauthorized_returns_message_shape(self):
        resp = self.client.get("/api/research/items")
        self.assertEqual(resp.status_code, 401)
        payload = resp.get_json()
        self.assertEqual(set(payload.keys()), {"message"})
        self.assertEqual(payload["message"], "token is missing")

    def test_iframe_headers_are_not_blocking(self):
        self._create_item("frame_headers")
        resp = self.client.get("/api/research/items", headers=self._auth_headers())
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.headers.get("X-Frame-Options"))
        self.assertEqual(resp.headers.get("Content-Security-Policy"), "frame-ancestors 'self'")


if __name__ == "__main__":
    unittest.main()
