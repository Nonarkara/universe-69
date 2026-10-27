"""The bounded harness must report extinctions even after a reseed."""
import importlib.util
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "sim"))
import engine

spec = importlib.util.spec_from_file_location("universe69_lab", os.path.join(ROOT, "tools", "lab.py"))
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class TestLabVerdict(unittest.TestCase):
    def test_reseed_does_not_erase_the_extinction_verdict(self):
        u = engine.genesis()["eden"]
        u["day"], u["iteration"] = 50000, 2
        u["postmortems"] = [{"day": 49000, "iteration": 1}]
        result = lab.verdict(u, "eden")
        self.assertTrue(result["completed"])
        self.assertIn("reseeded as iteration 2", result["verdict"])
        self.assertIn("day 49000", result["verdict"])
        self.assertNotIn("NEVER EMPTIED", result["verdict"])

    def test_an_unfinished_first_iteration_stays_unfinished(self):
        result = lab.verdict(engine.genesis()["eden"], "eden")
        self.assertFalse(result["completed"])
        self.assertIn("NEVER EMPTIED", result["verdict"])
