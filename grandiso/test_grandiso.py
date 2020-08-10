import unittest

from . import GrandIso


class TestGrandIso(unittest.TestCase):
    def test_can_create(self):
        GrandIso()

    def test_can_create_without_limits(self):
        self.assertEqual(GrandIso().limits.wallclock_limit_seconds, None)

    def test_is_not_ready_without_graph(self):
        g = GrandIso()
        self.assertEqual(g.is_ready(), False)
