import unittest

from src.game import Action, ActionType, BoardGameEngine, RuleError, create_mirror_opening


class TestGameEngine(unittest.TestCase):
    def test_move_and_turn_switch(self):
        state = create_mirror_opening()
        engine = BoardGameEngine(state)
        engine.submit_action("p1", Action("p1_u2", ActionType.MOVE, (2, 1)))
        self.assertEqual(state.current_player, "p2")
        self.assertEqual(state.units["p1_u2"].position, (2, 1))

    def test_invalid_out_of_turn(self):
        state = create_mirror_opening()
        engine = BoardGameEngine(state)
        with self.assertRaises(RuleError):
            engine.submit_action("p2", Action("p2_u1", ActionType.MOVE, (3, 4)))

    def test_skill_cooldown(self):
        state = create_mirror_opening()
        state.units["p1_u2"].position = (2, 1)
        state.units["p2_u2"].position = (2, 3)
        engine = BoardGameEngine(state)
        engine.submit_action("p1", Action("p1_u2", ActionType.SKILL, (2, 3)))
        self.assertEqual(state.units["p1_u2"].cooldown, 1)


if __name__ == "__main__":
    unittest.main()
