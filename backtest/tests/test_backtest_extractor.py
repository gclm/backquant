import json
import pickle
import tempfile
import unittest
from pathlib import Path

from app.backtest.services.extractor import extract_result


class _FakeSeries:
    def __init__(self, values):
        self._values = list(values)

    def tolist(self):
        return list(self._values)


class _FakeTable:
    def __init__(self, data: dict[str, list], index: list):
        self._data = {key: _FakeSeries(values) for key, values in data.items()}
        self.columns = list(data.keys())
        self.index = list(index)

    def __getitem__(self, key: str):
        return self._data[key]


class BacktestExtractorTestCase(unittest.TestCase):
    def test_extract_result_includes_benchmark_nav_from_benchmark_portfolio(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result_pkl = tmp_path / "result.pkl"
            out_json = tmp_path / "extracted.json"

            payload = {
                "summary": {"x": 1},
                "portfolio": _FakeTable(
                    {"unit_net_value": [1.0, 1.01], "returns": [0.0, 0.01]},
                    index=["2026-01-01", "2026-01-02"],
                ),
                "benchmark_portfolio": _FakeTable(
                    {"unit_net_value": [1.0, 1.005]},
                    index=["2026-01-01", "2026-01-02"],
                ),
                "trades": [],
            }
            result_pkl.write_bytes(pickle.dumps(payload))

            extracted = extract_result(result_pkl, out_json)
            self.assertEqual(extracted["equity"]["benchmark_nav"], [1.0, 1.005])
            self.assertEqual(extracted["trade_columns"], [])
            on_disk = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(on_disk["equity"]["benchmark_nav"], [1.0, 1.005])
            self.assertEqual(on_disk["trade_columns"], [])

    def test_extract_result_uses_benchmark_curve_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result_pkl = tmp_path / "result.pkl"
            out_json = tmp_path / "extracted.json"

            payload = {
                "summary": {},
                "portfolio": _FakeTable(
                    {"unit_net_value": [1.0], "returns": [0.0]},
                    index=["2026-01-01"],
                ),
                "benchmark_curve": {"nav": [1.0]},
            }
            result_pkl.write_bytes(pickle.dumps(payload))

            extracted = extract_result(result_pkl, out_json)
            self.assertEqual(extracted["equity"]["benchmark_nav"], [1.0])
