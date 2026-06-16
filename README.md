# SovHarn

> 开源的 Agent 工作台 — Open-Source Agent Harness Platform

一个轻量级的本地 AI Agent 框架，支持三级记忆系统、MCP 工具调用、权限控制和 Web 界面。

---

## 快速开始

```bash
python3 run.py
```

浏览器打开 http://127.0.0.1:8080

## 安装

```bash
pip install sovharn
sovharn
```

## 功能

- **三级记忆** — Session（会话）/ Daily（日维度）/ Permanent（永久）
- **Spec Engine** — YAML 定义输出标准，Agent 按规范执行
- **Gate Keeper** — 工具权限、内容安全控制
- **MCP 工具集成** — 支持 MCP Server 动态调用
- **Web UI** — 简洁的浏览器操作界面
- **技能系统** — 可插拔的技能插件，如 web-search

## 项目结构

```
├── sovharn/
│   ├── core/              # 核心模块
│   │   ├── memory.py      # 记忆系统
│   │   ├── spec_engine.py # 规范引擎
│   │   └── gate_keeper.py # 权限控制
│   └── api/               # API 层
│       ├── agents.py
│       ├── sessions.py
│       ├── memory.py
│       ├── skills.py
│       ├── settings.py
│       └── audit.py
├── frontend/              # Web 前端
├── data/                  # 本地数据存储
│   ├── specs/
│   ├── agents/
│   └── skills/
├── run.py                 # 启动入口
├── Dockerfile             # Docker 部署
└── pyproject.toml
```

## 数据

所有数据存储在 `./data/` 目录，不依赖外部数据库。

## License

MIT
