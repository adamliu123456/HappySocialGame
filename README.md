# HappySocialGame MVP

一个面向**社交对战**的可迭代原型仓库，当前聚焦：

- 原型B：异步回合「棋盘突袭」
- 轻量匹配与排位（Elo + 可扩展到 Glicko/TrueSkill）
- 可快速验证的服务端权威回合结算逻辑

## 快速开始

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 src/demo.py
```

## 目录

- `docs/PRODUCT_PLAN.md`：玩法、社交、排位、赛季与变现方案
- `src/game.py`：异步回合棋盘核心规则
- `src/matchmaking.py`：异步对战匹配队列（支持宽松时延）
- `src/rating.py`：排位算法抽象与 Elo 实现
- `src/demo.py`：本地演示脚本
- `tests/`：核心规则与排位测试
