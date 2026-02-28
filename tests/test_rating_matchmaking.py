import unittest

from src.matchmaking import MatchmakingQueue, PlayerTicket
from src.rating import EloRating, LadderProfile, settle_match_1v1


class TestRatingAndQueue(unittest.TestCase):
    def test_elo_settlement(self):
        elo = EloRating(k=32)
        a = LadderProfile("a", rating=1000)
        b = LadderProfile("b", rating=1000)
        settle_match_1v1(a, b, elo)
        self.assertGreater(a.rating, 1000)
        self.assertLess(b.rating, 1000)

    def test_newbie_pool_split(self):
        q = MatchmakingQueue(base_window=100, newbie_limit=10)
        q.enqueue(PlayerTicket("new", 1000, newbie_games=2))
        q.enqueue(PlayerTicket("old", 1000, newbie_games=20))
        self.assertIsNone(q.pop_match())

    def test_wait_expands_window(self):
        q = MatchmakingQueue(base_window=50)
        q.enqueue(PlayerTicket("a", 1000, newbie_games=20, wait_seconds=0))
        q.enqueue(PlayerTicket("b", 1090, newbie_games=20, wait_seconds=0))
        self.assertIsNone(q.pop_match())
        q.tick(15)
        self.assertIsNotNone(q.pop_match())


if __name__ == "__main__":
    unittest.main()
