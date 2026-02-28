# HappySocialGame（社交对战游戏 MVP）

这是一个可直接运行与游玩的社交对战游戏 MVP，基于你建议的**原型B：异步回合“棋盘突袭”**，并补齐了：

- 可交互 CLI 对战（玩家 vs AI）
- 自动演示模式（bot vs bot）
- 代码生成像素美术资产（PPM）
- 基础排位与社交模块

## 玩法（当前可玩版本）

- 棋盘：5x5
- 单位：`scout`（机动） / `bruiser`（高血）
- 回合：双方各提交 1 个行动（移动 + 可选技能）
- 据点：占领 `*` 点位每回合加分
- 胜负：
  - 击杀到对手无单位
  - 或先到 6 分
  - 或回合结束（12 回合）按分数决胜

## 运行方式

### 1) 运行交互版（推荐）

```bash
python3 main.py
```

### 2) 运行自动演示（无交互）

```bash
python3 main.py --auto
```

## 代码生成美术资产

本项目提供代码绘制像素风资产（输出到 `assets/generated`，格式 PPM）：

```bash
python3 tools/generate_assets.py
```

当前生成：
- `unit_scout.ppm`
- `unit_bruiser.ppm`
- `control_point.ppm`

## 项目结构

- `social_game/engine.py`：回合战斗规则与结算
- `social_game/ai.py`：AI 策略（占点 + 近战倾向）
- `social_game/render.py`：终端棋盘渲染
- `social_game/rating.py`：Elo + TrueSkillLite
- `social_game/social.py`：好友/公会/回放基础能力
- `tools/generate_assets.py`：代码生成美术资产
- `tests/test_engine.py`：核心回归测试

## 下一步可扩展

1. 接 WebSocket/REST，把异步回合提交改为服务化。
2. 加入账号、公会赛季与战报页。
3. 把 PPM 资产接入前端（例如 pygame 或 Web 前端）。
4. 增加“新手房 + 教学关 + 推荐卡组/阵容”。
