# Timer: Your AI-powered scheduling sidekick—create, track, and manage tasks effortlessly with a smart, interactive companion

## 🧑🏻‍💻 Usage

通过 [Web Page](timer-frontends-a12f7h6lc-whizhous-projects-7cb8caf3.vercel.app) 使用 Timer

## 📚 Ready to Development

建议首先阅读并完善 [docs](/docs) 中的文档

关于后端的详细信息请阅读 [README.md](/backends/README.md)

## 🛠️ Installation

Clone this repo:

```
git clone ...
```

See [INSTALL.md](./INSTALL.md) for installation instructions.

## 📂 概览

以下为项目结构示例：

```
.
├backends/
├── app/                       # Flask 应用核心
│   ├── __init__.py            # 应用工厂函数 create_app()
│   ├── extensions.py          # 扩展初始化（如数据库、缓存）
│   └── config.py              # 配置类（Dev/Prod/Test）
│
├── core/                      # 业务逻辑
│   ├── scheduler.py           # Scheduler 接口
│   ├── schedule_manager.py    # ScheduleManager (JSON)
│   └── ai_scheduler.py        # AIScheduler (DeepSeek)
│
├── routes/                    # 路由模块（改用蓝图）
│   ├── schedule.py            # 日程管理蓝图
│   └── ai.py                  # AI 交互蓝图
│
├── utils/                     # 工具函数（不变）
│   ├── file_utils.py
│   └── ai_utils.py
│
├── tests/                     # 测试（适配工厂模式）
│   ├── conftest.py            # pytest 夹具（fixtures）
│   └── test_schedule.py
├─docs
├─frontends
└─pet
```
