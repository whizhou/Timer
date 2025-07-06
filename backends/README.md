# Timer Backends

Contain backend codes for Timer

已经完成了基本的日程管理功能，可以完成创建、修改、删除、归档等操作。完成了AI Agent以及大模型对话接口。

目前已通过 PythonAnywhere，完成了后端的生产部署。

## 运行后端

运行以下指令，之后可以看到命令行输出后端地址，一般为 `http://127.0.0.1:5000`

```
conda activate Timer
cd backends/
flask run
```

可以直接通过网页查看输出的过程（因为现在都是输出 example），如

```
http://127.0.0.1:5000/schedule
http://127.0.0.1:5000/schedule/1
http://127.0.0.1:5000/schedule/archive/2
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

具体接口文档见 [Backends_API.md](../docs/Backends_API.md)

与后端的所有交互 *目前* 都使用 json 格式，包括上传和接受消息

接口定义代码位于 [routes/](/backends/routes/)，其中 

+ [schedule_routes.py](/backends/routes/schedule_routes.py) 定义了基本日程管理操作的接口；
+ [chat_routes.py](/backends/routes/chat_routes.py) 定义了大模型对话相关接口。

具体交互方式可以参考测试代码 [test_routes.py](/backends/tests/test_schedule_routes.py) 和 [test_chat.py](/backends/tests/test_chat.py)

## 测试

```sh
cd backends/
pytest -k "schedule"  # 测试 shedule_routes 模块
pytest -k "chat"  # 测试 chat 模块，需要调用 Deepseek API，需要一定时间
```

```sh
cd backends/tests
python chat_individual.py  # 测试 requests 库调用 chat 模块并保持上下文
```
