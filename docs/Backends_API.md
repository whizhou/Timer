# 后端接口声明

此文档详细说明了后端接口的调用

调试环境下，所有后端接口的调用格式均为 `http:/127.0.0.1:5000/` + 功能url 的格式

## Schedule Routes

`schedule_routes` 的前缀为 /schedule，即所有url都由此前缀开始，上一版的后端接口文档有部分接口未写明此前缀，请注意。

返回值中，大致有如下 key-value 键值对：

+ `schedules: []` 多个日程列表

+ `schedule: {}` 单个日程信息

+ `ids: []` 日程 id 列表

+ `success: bool` 操作是否成功

+ `error: str` 错误信息

### URL: `/schedule`

+ **Methods**: `GET` - 获取所有日程 (not archived)

  + **Response**

    返回所有日程

    ```json
    {
        {
        "schedules": [
          {
            "id": "the id of the schedule",
            "timestamp": "last modified time, in YYYY-MM-DD HH:MM:SS format",
            "type": "schedule",
            "content": {
              "title": "the title of the schedule",
              "content": "the content of the schedule (optional)",
              "whole_day": "bool: whether the schedule is a whole day event",
              "begin_time": ["YYYY-MM-DD", "HH:MM (default 08:00)"],
              "end_time": ["YYYY-MM-DD", "HH:MM (default 23:59)"],
              "location": "the location of the schedule (optional)",
              "remind_before": "the time (in minutes) to remind before the schedule starts (optional)",
              "tag": "the tag of the schedule (optional)",
              "repeat": {
                  "repeat": "bool: whether the schedule is a repeat event",
                  "type": "the type of repeat (e.g., daily, weekly, monthly) (optional)",
                  "every": "the interval of repeat (e.g., 1) (optional)",
                  "repeat_until": ["YYYY-MM-DD", "HH:MM (default 23:59)"]
              },
              "additional_info": [
                  "any additional information related to the schedule (optional)",
                  "this can include links, notes, or any other relevant details",
                  "without any specific format, just plain text"
              ]
            }
          },
          {
            "id": 1
          }
        ]
        }
    }
    ```

+ **Methods**: `POST` - 创建日程

  可以传入多个日程，对于传入日程，检查是否有 `id` 和 `timestamp`。
  
  如果 `id=-1` 或者缺失，则根据已有日程分配一个独一的 `id`；否则使用传入 `id` （暂未实现冲突检测）。

  如果 `timestamp` 缺失，则根据当前时间设置；否则使用传入时间戳。

  + **Requests**

    ```json
    {"schedules": []}
    ```

  + **Response**

    返回成功创建的日程 id （按传入顺序）

    ```json
    {"ids": [1, 2, 3]}
    ```

### URL: `/schedule/<int:id>`

+ **Methods**: `GET` - 根据 `id` 获取单个日程

  + **Response**

    ```json
    {"schedule": {}}
    ```

    注意 "schedule" 为单个日程信息，不用 `[]` 包裹为列表。

+ **Methos**: `PUT` - 根据传入 `schedule` 全量更新（覆盖）本地日程

  + **Requests**

    ```json
    {"schedule": {}}
    ```

  + **Response**

    返回是否成功

    ```json
    {"success": true}
    ```

+ **Methods**: `DELETE` - 根据 `id` 删除日程

  + **Response**

    ```json
    {"success": true}
    ```

### URL: `/schedule/archive/<int:id>`

+ **Methods**: `GET` - 根据 `id` 归档日程（标记完成）

  + **Response**

    ```json
    {"success": true}
    ```

### URL: `/schedule/remind_start`

+ **Methods**: `GET` - 获取设置了每日提醒（从某一日期开始）

  + **Response**

    返回所有已经开始每日提醒的日程

    ```json
    {"schedules": []}
    ```

### URL: `/schedule/remind_before`

+ **Methods**: `GET` - 获取设置了提前提醒（开始时间前提醒）

  + **Response**

    返回所有到达提前提醒时间的日程

    ```json
    {"shedules": {}}
    ```

### URL: `/schedule/sync`

+ **Methods**: `GET` - 同步传入日程

  + **Requests**

    同步传入所有日程，根据 `id` 和 `timestamp` 更新本地日程。

    如果传入日程 `id=-1` 或者 `id` 在已有日程库中无匹配，则按照创建日程逻辑添加本地日程；

    如果传入日程 `timestamp` 较本地时间戳更新，则用传入日程信息 **覆盖** 本地日程

    ```json
    {"schedules": []}
    ```

  + **Response**

    返回同步后的所有本地日程

    ```json
    {"schedules": []}
    ```

### URL: `/schedule/quantity`

+ **Methods**：`GET` - 获取日程数量

  + **Response**

  返回本地存储的日程数量（未归档日程）

  ```json
  {"quantity": 123}
  ```

### URL: `/schedule/quantity/<int:days>`

+ **Methods**: `GET` - 获取 days 天的日程数量

  + **Response**：同上

### URL: `/schedule/titles/<int:days>`

+ **Methods**: `GET` - 获取 days 天的日程标题

  + **Response**

    返回改天的所有未归档日程的标题列表

    ```json
    {"titles": []}
    ```

## Auth Routes

url prefix: `/auth`

实现登录功能后，后端会对前端的每次访问验证 cookie 中的 `user_id`。
如果 cookie 中不包含 `user_id` 信息或者信息不正确，则会直接返回报错信息：

```json
{"success": false, "error": "error infomation"}
```

### URL: `/auth/register`

+ **Methods**: `POST` - 用户注册

  实现用户注册功能，返回注册是否成功；如果失败则包含 `error`

  + **Requests**:

    通过 POST 方法直接传入 `username` 和 `password`

    ```json
    {"username": "user", "password": 123}
    ```

  + **Response**:

    如果成功 (`success=true`) 则不包含报错信息 `error`

    ```json
    {"success": false, "error": "Invalid request method."}
    ```

### URL: `/auth/login`

+ **Methods**: `POST` - 用户登录

  验证 `username` 和 `password`，返回是否登录成功，并在 cookie 中隐式包含 `user_id` 用于后续访问。

  + **Requests**:

    通过 POST 方法直接传入 `username` 和 `password`

    ```json
    {"username": "user", "password": 123}
    ```

  + **Response**:

    如果成功 (`success=true`) 则不包含报错信息 `error`

    ```json
    {"success": false, "error": "Invalid request method."}
    ```

    成功登录后，会在 cookie 中隐式返回 `user_id`，需要在后续范围中携带，否则会认为是未登录。

