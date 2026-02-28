from social_battle.core import (
    Board,
    MonetizationPlan,
    Player,
    Terrain,
    TurnAction,
    resolve_turn,
    trueskill_like_quality,
    update_elo,
)


def test_move_and_attack_with_terrain_defense() -> None:
    board = Board(3, 3, terrain=[
        [Terrain.PLAIN, Terrain.PLAIN, Terrain.PLAIN],
        [Terrain.PLAIN, Terrain.FORT, Terrain.PLAIN],
        [Terrain.PLAIN, Terrain.PLAIN, Terrain.PLAIN],
    ])
    a = Player("1", "Alice", position=(0, 1))
    b = Player("2", "Bob", position=(1, 1))

    resolve_turn(board, a, b, TurnAction(attack=True))

    # 基础伤害2，堡垒减伤2，最少1点
    assert b.hp == 9


def test_elo_update_changes_both_players() -> None:
    a = Player("1", "A", rating=1200)
    b = Player("2", "B", rating=1200)

    update_elo(a, b, a_win=1)

    assert a.rating > 1200
    assert b.rating < 1200


def test_trueskill_like_quality_range() -> None:
    q = trueskill_like_quality([25, 26, 24, 25], [8, 8, 9, 8])
    assert 0 < q <= 1


def test_monetization_validation() -> None:
    plan = MonetizationPlan(pure_cosmetic=False, has_lootbox=True, probability_disclosure_required=False)
    issues = plan.validate()
    assert len(issues) == 2
