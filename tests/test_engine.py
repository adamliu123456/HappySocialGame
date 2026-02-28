import unittest

from social_game.ai import BotPolicy
from social_game.engine import GameRoom, PlayerAction
from social_game.render import render_board


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
        self.assertIn("control_points", snap)

    def test_bot_policy_returns_valid_action(self):
        room = GameRoom("r1", "p1", "p2")
        bot = BotPolicy("p2")
        action = bot.choose_action(room)
        self.assertEqual(action.player_id, "p2")
        self.assertGreaterEqual(action.unit_index, 0)

    def test_render_board_has_coordinates(self):
        room = GameRoom("r1", "p1", "p2")
        board = render_board(room, "p1", "p2")
        self.assertIn("0 1 2 3 4", board)


if __name__ == "__main__":
    unittest.main()
