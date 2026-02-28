from __future__ import annotations

import argparse

from social_game import BotPolicy, EloRating, GameRoom, PlayerAction, render_board


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Happy Social Game CLI MVP")
    p.add_argument("--auto", action="store_true", help="run bot vs bot non-interactive demo")
    return p.parse_args()


def choose_player_action(room: GameRoom, player_id: str) -> PlayerAction:
    while True:
        print(render_board(room, player_id, next(pid for pid in room.players if pid != player_id)))
        print(f"\n{player_id} 的回合：请选择单位与目的地")
        units = room.players[player_id].units
        for i, unit in enumerate(units):
            print(f"  [{i}] {unit.unit_type.value} hp={unit.hp} pos=({unit.x},{unit.y}) skill_used={unit.skill_used}")

        try:
            unit_index = int(input("单位编号: ").strip())
            tx = int(input("目标X: ").strip())
            ty = int(input("目标Y: ").strip())
            use_skill = input("是否用技能加伤? (y/N): ").strip().lower() == "y"
            action = PlayerAction(player_id, unit_index, tx, ty, use_skill=use_skill)
            room.submit_action(action)
            return action
        except Exception as err:  # noqa: BLE001
            print(f"输入无效：{err}，请重试。\n")


def run_game(auto: bool = False) -> None:
    room = GameRoom("room-mvp-001", "you", "bot")
    bot = BotPolicy("bot")
    ally_bot = BotPolicy("you")

    print("=== Happy Social Game CLI MVP ===")
    print("目标：占点得分或击败对手，先到 6 分或回合结束分高者胜。\n")

    while True:
        if auto:
            room.submit_action(ally_bot.choose_action(room))
        else:
            choose_player_action(room, "you")

        room.submit_action(bot.choose_action(room))
        result = room.resolve_turn()

        print("\n--- 回合结算 ---")
        for event in result.events:
            print("-", event)
        print("比分:", room.score)
        print(render_board(room, "you", "bot"))

        if result.winner:
            print("\n胜者:", result.winner)
            elo = EloRating()
            ra, rb = elo.update(1200, 1200, 1.0 if result.winner == "you" else 0.0)
            print(f"Elo 更新: you={ra:.1f}, bot={rb:.1f}")
            break


def main() -> None:
    args = parse_args()
    run_game(auto=args.auto)


if __name__ == "__main__":
    main()
