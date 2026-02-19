import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from flask import Flask

from app.backtest.services.runner import run_rqalpha


class BacktestRunnerTestCase(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self._tmpdir.name)

        app = Flask(__name__)
        app.config.update(
            BACKTEST_BASE_DIR=str(self.base_dir),
            RQALPHA_BUNDLE_PATH="/tmp",
            BACKTEST_TIMEOUT=1,
            RQALPHA_COMMAND="",
            TESTING=True,
        )
        self.app = app

    def tearDown(self):
        self._tmpdir.cleanup()

    def _build_job_dir(self, job_id: str = "job1") -> Path:
        job_dir = self.base_dir / "runs" / "2026-02-16" / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    @staticmethod
    def _build_proc() -> Mock:
        proc = Mock()
        proc.wait.return_value = 0
        proc.poll.return_value = 0
        return proc

    def test_run_rqalpha_uses_binary_in_path_when_available(self):
        job_dir = self._build_job_dir("job_binary")
        proc = self._build_proc()

        with self.app.app_context(), patch(
            "app.backtest.services.runner.shutil.which",
            return_value="/usr/local/bin/rqalpha",
        ), patch("app.backtest.services.runner.subprocess.Popen", return_value=proc) as popen:
            code = run_rqalpha("job_binary", job_dir)

        self.assertEqual(code, 0)
        cmd = popen.call_args.args[0]
        self.assertEqual(
            cmd,
            ["/usr/local/bin/rqalpha", "run", "-f", "strategy.py", "--config", "config.yml"],
        )

    def test_run_rqalpha_falls_back_to_python_module_when_binary_missing(self):
        job_dir = self._build_job_dir("job_module")
        proc = self._build_proc()

        with self.app.app_context(), patch(
            "app.backtest.services.runner.shutil.which",
            return_value=None,
        ), patch("app.backtest.services.runner.subprocess.Popen", return_value=proc) as popen:
            code = run_rqalpha("job_module", job_dir)

        self.assertEqual(code, 0)
        cmd = popen.call_args.args[0]
        self.assertEqual(
            cmd,
            [sys.executable, "-m", "rqalpha", "run", "-f", "strategy.py", "--config", "config.yml"],
        )

    def test_run_rqalpha_prefers_configured_command(self):
        job_dir = self._build_job_dir("job_custom")
        proc = self._build_proc()
        self.app.config["RQALPHA_COMMAND"] = "custom-rqalpha --foo"

        with self.app.app_context(), patch(
            "app.backtest.services.runner.shutil.which",
            return_value="/usr/local/bin/rqalpha",
        ), patch("app.backtest.services.runner.subprocess.Popen", return_value=proc) as popen:
            code = run_rqalpha("job_custom", job_dir)

        self.assertEqual(code, 0)
        cmd = popen.call_args.args[0]
        self.assertEqual(
            cmd,
            ["custom-rqalpha", "--foo", "run", "-f", "strategy.py", "--config", "config.yml"],
        )


if __name__ == "__main__":
    unittest.main()
