import unittest

from social_game.engine import GameRoom, PlayerAction


class EngineTests(unittest.TestCase):
    def test_turn_resolution_increments_turn_and_events(self):
        room = GameRoom("r1", "p1", "p2")
        room.submit_action(PlayerAction("p1", 0, 1, 0))
        room.submit_action(PlayerAction("p2", 0, 3, 4))
        result = room.resolve_turn()

        self.assertEqual(room.turn, 2)
        self.assertTrue(result.events)

    def test_snapshot_contains_players_and_score(self):
        room = GameRoom("r1", "p1", "p2")
        snap = room.snapshot()
        self.assertIn("players", snap)
        self.assertIn("score", snap)


if __name__ == "__main__":
    unittest.main()
