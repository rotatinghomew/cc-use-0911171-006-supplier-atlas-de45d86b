import copy
import json
import unittest
from pathlib import Path
from app import inspect
from records import load


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.data = copy.deepcopy(load(Path(__file__).parents[1] / "fixtures/data.json"))
        self.day = "2026-10-31"

    def test_end_to_end_inspection_is_json_and_repeatable(self):
        before = copy.deepcopy(self.data)
        first = inspect(self.data, self.day)
        self.assertEqual(first, inspect(self.data, self.day))
        self.assertEqual(before, self.data)
        self.assertTrue(json.dumps(first, ensure_ascii=False, allow_nan=False))

    def test_missing_history_is_null(self):
        from profiles import build
        rows = {row["supplier"]: row for row in build(self.data, self.day)["rows"]}
        self.assertIsNone(rows["V38"]["on_time_rate"])
        self.assertEqual(rows["V38"]["deliveries"], 0)

    def test_manual_membership_is_distinguishable(self):
        from segments import effective_members
        rows = {row["supplier"]: row for row in effective_members(self.data, self.day)["assignments"]}
        self.assertEqual(rows["V36"]["group"], "stable")
        self.assertEqual(rows["V36"]["data_group"], "new")

    def test_strategy_follows_effective_group(self):
        from strategies import dispatch
        row = next(row for row in dispatch(self.data, self.day)["actions"] if row["supplier"] == "V36")
        self.assertEqual(row["inspection_fraction"], .05)
        self.assertTrue(row["manual"])

    def test_version_links_match(self):
        from profiles import build
        from strategies import dispatch
        self.assertEqual(build(self.data, self.day)["profile_id"], dispatch(self.data, self.day)["profile_id"])

    def test_unknown_strategy_rejected(self):
        from strategies import dispatch
        self.data["strategies"] = []
        with self.assertRaises(ValueError):
            dispatch(self.data, self.day)

    def test_future_delivery_not_used(self):
        from profiles import build
        before = build(self.data, self.day)
        self.data["deliveries"].append({**self.data["deliveries"][0], "recorded_at": "2027-01-01", "received_kg": 9999})
        self.assertEqual(before, build(self.data, self.day))

    def test_mixed_quality_stays_at_load_level(self):
        from profiles import mixed_exposure
        evidence = mixed_exposure(self.data, self.day)
        self.assertEqual(evidence["loads"][0]["suppliers"], ["V01", "V02"])
        self.assertEqual(evidence["independent_rechecks"], [])
