from social_game.engine import GameRoom, PlayerAction
from social_game.rating import EloRating
from social_game.social import SocialHub


def run_demo() -> None:
    room = GameRoom("room-001", "alice", "bob")
    social = SocialHub()
    social.add_friend("alice", "bob")

    alice_plan = [(1, 0), (2, 1), (2, 2), (2, 2), (2, 2)]
    bob_plan = [(3, 4), (2, 3), (2, 2), (2, 2), (2, 2)]

    print("=== Happy Social Game: Prototype B Demo ===")
    for turn_idx in range(len(alice_plan)):
        ax, ay = alice_plan[turn_idx]
        bx, by = bob_plan[turn_idx]
        room.submit_action(PlayerAction("alice", 0, ax, ay, use_skill=(turn_idx >= 2)))
        room.submit_action(PlayerAction("bob", 0, bx, by, use_skill=(turn_idx >= 2)))
        result = room.resolve_turn()

        for event in result.events:
            social.save_replay_event(room.room_id, event)
            print("-", event)
        print("snapshot:", room.snapshot())

        if result.winner:
            break

    winner = result.winner or max(room.score, key=room.score.get)
    print("winner:", winner)
    elo = EloRating()
    ra, rb = elo.update(1200, 1200, 1.0 if winner == "alice" else 0.0)
    print(f"elo update => alice: {ra:.1f}, bob: {rb:.1f}")


if __name__ == "__main__":
    run_demo()
