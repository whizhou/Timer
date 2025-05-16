# Timer Backends

Contain backend codes for Timer

## 运行后端

运行以下指令，之后可以看到命令行输出后端地址，一般为 `http://127.0.0.1:5000`

```
conda activate Timer
cd backends/
flask run
```

## 后端代码结构

```
.
├── app
├── config
├── core
├── data
│   └── chat_session
├── flask_session
├── routes
└── tests
```

注释：

+ `app/` 下定义了 Flask 应用工厂，实现应用的启动和初始化
+ `config/` 下定义了应用 settings。注意敏感信息如 APIKEY 不要提交到 Git
+ `core/` 包含主题构件
+ `data/` 包含后端数据，如日程信息，用户信息等。除了 `example` 不应当提交到 Git
+ `routes/` 定义了 Flask 路由，包含前端接口和构建接口等
+ `tests/` 包含测试代码


## 接口文档

> 目前接口的交互方式还不统一，包括：
> 
> 1. 交互方式不统一，部分接口使用 `json` 交互，但是部分接口直接使用 `data` 属性传输文件
> 
> 2. 文件格式不统一，交互文件 (主要为 `dict`) 的格式还没有统一规定。
>
> 交互方式和前后端代码逻辑有关，大概原则是减少数据大小、方便前端代码编写。~~日后商榷~~

接口定义代码位于 [routes/](/backends/routes/)，其中 

+ [schedule_routes.py](/backends/routes/schedule_routes.py) 定义了基本日程管理操作的接口；
+ [chat_routes.py](/backends/routes/chat_routes.py) 定义了大模型对话相关接口。

具体交互方式可以参考测试代码 [test_routes.py](/backends/tests/test_schedule_routes.py) 和 [test_chat.py](/backends/tests/test_chat.py)

目前 `chat` 功能为普通的大模型对话，后端会保存所有对话历史到本地文件系统 (路径 `backends/data/chat_session`)

对于多轮对话，使用 cookie 的 session-id 区分不同的对话历史。对于桌宠调用，可以参考 [chat_individual.py](/backends/tests/chat_individual.py) 进行调用。

## 测试

```
cd backends/
pytest
```

```
cd backends/tests
python chat_individual.py
```