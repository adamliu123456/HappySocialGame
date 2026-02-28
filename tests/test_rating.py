import unittest

from src.happysocialgame.rating import EloRating, Glicko2Player, update_multiplayer_ratings


class TestRating(unittest.TestCase):
    def test_elo_update(self):
        a = EloRating(1500)
        b = EloRating(1500)
        a2 = a.update(b, actual_score=1.0)
        self.assertGreater(a2.value, a.value)

    def test_glicko2_update(self):
        p = Glicko2Player(rating=1500, rd=200)
        opponents = [
            (Glicko2Player(rating=1400, rd=30), 1.0),
            (Glicko2Player(rating=1550, rd=100), 0.0),
            (Glicko2Player(rating=1700, rd=300), 0.0),
        ]
        p2 = p.update(opponents)
        self.assertNotEqual(p.rating, p2.rating)
        self.assertLess(p2.rd, p.rd)

    def test_multiplayer_update(self):
        ratings = [1500, 1500, 1500, 1500]
        ranks = [1, 2, 3, 4]
        new_ratings = update_multiplayer_ratings(ratings, ranks)
        self.assertGreater(new_ratings[0], ratings[0])
        self.assertLess(new_ratings[3], ratings[3])


if __name__ == "__main__":
    unittest.main()
