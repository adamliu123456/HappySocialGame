import time
import unittest

from src.happysocialgame.matchmaking import MatchTicket, Matchmaker


class TestMatchmaking(unittest.TestCase):
    def test_basic_match(self):
        mm = Matchmaker()
        mm.enqueue(MatchTicket("p1", 1500, "ranked_1v1"))
        mm.enqueue(MatchTicket("p2", 1540, "ranked_1v1"))

        match = mm.pop_match("ranked_1v1", 2)
        self.assertIsNotNone(match)
        self.assertEqual(mm.queue_size("ranked_1v1"), 0)

    def test_window_expansion(self):
        mm = Matchmaker()
        old = MatchTicket("p1", 1500, "ranked_1v1", created_at=time.time() - 45)
        mm.enqueue(old)
        mm.enqueue(MatchTicket("p2", 1620, "ranked_1v1"))

        match = mm.pop_match("ranked_1v1", 2)
        self.assertIsNotNone(match)


if __name__ == "__main__":
    unittest.main()
