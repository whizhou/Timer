# 后端接口声明

此文档详细说明了后端接口的调用

调试环境下，所有后端接口的调用格式均为 `http:/127.0.0.1:5000/` + 功能url 的格式

## Schedule Routes

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

### URL: `/archive/<int:id>`

+ **Methods**: `GET` - 根据 `id` 归档日程（标记完成）

  + **Response**

    ```json
    {"success": true}
    ```

### URL: `/remind_start`

+ **Methods**: `GET` - 获取设置了每日提醒（从某一日期开始）

  + **Response**

    返回所有已经开始每日提醒的日程

    ```json
    {"schedules": []}
    ```

### URL: `/remind_before`

+ **Methods**: `GET` - 获取设置了提前提醒（开始时间前提醒）

  + **Response**

    返回所有到达提前提醒时间的日程

    ```json
    {"shedules": {}}
    ```

### URL: `/sync`

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

### URL: `/quantity`

+ **Methods**：`GET` - 获取日程数量

  + **Response**

  返回本地存储的日程数量（未归档日程）

  ```json
  {"quantity": 123}
  ```
