from game import Action, ActionType, BoardGameEngine, create_mirror_opening
from rating import EloRating, LadderProfile, settle_match_1v1


def run_demo() -> None:
    state = create_mirror_opening()
    engine = BoardGameEngine(state)

    engine.submit_action("p1", Action("p1_u2", ActionType.MOVE, (2, 1)))
    engine.submit_action("p2", Action("p2_u2", ActionType.MOVE, (2, 3)))
    engine.submit_action("p1", Action("p1_u2", ActionType.SKILL, (2, 3)))

    print("=== Turn Log ===")
    for line in state.turn_log:
        print(line)

    elo = EloRating(k=24)
    p1 = LadderProfile("p1", rating=1012)
    p2 = LadderProfile("p2", rating=998)
    settle_match_1v1(p1, p2, elo)
    print("=== Ratings ===")
    print(f"p1={p1.rating}, p2={p2.rating}")


if __name__ == "__main__":
    run_demo()
