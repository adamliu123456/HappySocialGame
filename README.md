# HappySocialGame MVP

这是一个面向**社交对战游戏**的 MVP 代码与策划蓝图，基于你给出的玩法原型整理而成。

## 我们选择的落地路线

优先实现 **原型 B：异步回合“棋盘突袭”**，并预留向公会赛季战（原型 E）扩展的能力：

- 异步/回合制降低了网络同步与反作弊复杂度。
- 支持“短回合 + 可异步提交”，适合碎片化用户。
- 赛季排名、好友挑战、公会周赛都容易叠加。

## 仓库内容

- `docs/game_design.md`：完整玩法、系统、运营、合规与里程碑。
- `src/happysocialgame/rating.py`：Elo / Glicko-2 / 多人简化评分更新。
- `src/happysocialgame/matchmaking.py`：面向 1v1/2v2/多人房间的匹配池实现。
- `src/happysocialgame/progression.py`：战斗通行证与纯外观经济层的基础模型。
- `tests/`：核心系统单元测试。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
python -m unittest discover -s tests -v
```

## 设计原则

1. **公平优先**：付费不影响战斗数值。
2. **社交驱动**：好友、公会、观战、回放分享贯穿系统。
3. **可运营**：赛季任务 + 活动 + 皮肤体系构建长期留存。
4. **可合规**：若使用随机抽取，必须披露概率与规则。
