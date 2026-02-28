import unittest

from src.happysocialgame.progression import BattlePass, SeasonTask


class TestProgression(unittest.TestCase):
    def test_task_completion_gives_xp(self):
        bp = BattlePass(season_id="s1")
        bp.add_task(SeasonTask("t1", "Win 3 games", target=3, reward_xp=200))
        gained = bp.report_task_progress("t1", 3)

        self.assertEqual(gained, 200)
        self.assertEqual(bp.level, 1)
        self.assertEqual(bp.xp, 200)

    def test_level_up(self):
        bp = BattlePass(season_id="s1", xp_per_level=100)
        bp.add_xp(250)

        self.assertEqual(bp.level, 3)
        self.assertEqual(bp.xp, 50)


if __name__ == "__main__":
    unittest.main()
