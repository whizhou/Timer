# Timer Backends

Contain backend codes for Timer

## 运行后端

运行以下指令，之后可以看到命令行输出后端地址，一般为 `http://127.0.0.1:5000`

```
conda activate Timer
cd backends/
flask run
```\

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

与后端的所有交互 *目前* 都使用 json 格式，包括上传和接受消息

接口定义代码位于 [routes/](/backends/routes/)，其中 

+ [schedule_routes.py](/backends/routes/schedule_routes.py) 定义了基本日程管理操作的接口；
+ [chat_routes.py](/backends/routes/chat_routes.py) 定义了大模型对话相关接口。

具体交互方式可以参考测试代码 [test_routes.py](/backends/tests/test_schedule_routes.py) 和 [test_chat.py](/backends/tests/test_chat.py)

目前 `chat` 功能为普通的大模型对话，后端会保存所有对话历史到本地文件系统 (路径 `backends/data/chat_session`)

对于多轮对话，使用 cookie 的 session-id 区分不同的对话历史。对于桌宠调用，可以参考 [chat_individual.py](/backends/tests/chat_individual.py) 进行调用。

## 测试

```
cd backends/
pytest -s  # 由于需要调用api，可能时间较久
```

```
cd backends/tests
python chat_individual.py
```