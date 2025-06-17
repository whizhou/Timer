# 接口说明

以下是针对 `AIScheduler` 类中 `process_user_request` 方法的接口说明文档：

---

# 接口说明：process_user_request

## 基本信息

**接口名称**：处理用户AI请求

**所属类**：`AIScheduler`

**方法签名**：`process_user_request(user_input: Dict) -> Union[Dict, str]`

**版本**：v1.0

**依赖组件**：

- `IntentClassifier`（意图分类器）
- `DeepSeekChat`（大模型对话历史管理）
- `AIScheduleManager`（AI日程管理）

---

## 功能描述

此接口是AI日程调度系统的核心入口，负责：

1. 接收多模态用户输入（文本/语音/图像）
2. 自动识别用户意图（创建/修改/删除/通用对话）
3. 路由到对应的处理逻辑
4. 返回结构化结果或自然语言响应

---

## 请求规范

### 输入参数

| 参数名       | 类型    | 必填 | 描述 |
| `user_input` | `Dict` |   是 | 用户输入字典Dict，包含”image” , ”voice” , ”word ”三项 |

### 输入示例

```python
{
    "word": "请帮我修改周三的会议到周四上午",
    "voice": "", 
    "image": "" 
}

```

---

## 响应规范

### 成功响应

根据意图类型返回不同结构：

### 1. 特定意图响应（CREATE）

```python
        return {
            "status": "success",
            "action": "create",
            "type": schedule_type, # 日志类型: reminder 或 scheduler
            "schedule_data": creation_result,  # 完整的创建数据
        }
```

```python
        if "error" in creation_result:
            return {
                "status": "error",
                "action": "create",
                "error": creation_result["error"] 
                # 返回一个字符串，说明问题
                # 有可能是创建类型无法识别，或者其他导致中断的问题
            }
```

### 2. 特定意图响应（MODIFY）

```python
        return {
            "status": "success",
            "action": "modify",
            "schedule_id": schedule_id, # int类型的id
            "original": original_data, # 完整的原始日志
            "modified": modified_data # 完整的修改后日志
        }
```

```python
        # 如果处理结果中有错误，返回错误信息
        if "error" in modification_result:
            return {
                "status": "error",
                "error": modification_result["error"]
                # 返回 "响应格式无效"
            }
```

### 3. 特定意图响应（DELETE）

```python
        return {
            "status": "success",
            "action": "delete",
            "schedule_id": schedule_id, # 被删除的日志的id（int类型）
            "schedule_title": schedule_title # 被删除日志的title(str类型)
        }
```

```python
        if "error" in deletion_result:
            return {
                "status": "error",
                "action": "delete",
                "error": deletion_result["error"]
                # 返回可能的str类型的错误信息
            }
```

### 4. 通用对话响应

返回自然语言字符串（str类型）：

```
"已为您将周三的会议调整到周四上午10点"

```

### 错误响应

```python
return "我无法处理您的请求，请稍后再试。"
```

---

## 意图处理逻辑

| 意图类型  | 处理流程 | 典型用户输入 |
| --- | --- | --- |
| `CREATE` | 1. 生成创建提示词. 调用LLM解析. 写入数据库 | "下周一下午3点安排体检" |
| `MODIFY` | 1. 检索现有日程. 生成差异提示. 执行更新 | "把会议改到明天早上" |
| `DELETE` | 1. 识别目标日程. 确认删除 | "取消本周所有会议" |
| `GENERAL` | 1. 语义分析. 生成自然回复 | "我下周有什么安排？" |

---

## 调用示例

### Python调用

```python
scheduler = AIScheduler(app)
response = scheduler.process_user_request(
    {"word": "明天上午10点创建产品评审会"}
)

```

---

## 注意事项

1. 输入字典至少需要包含`word`/`voice`/`image`中的一个字段
2. 系统会自动记录对话历史以实现上下文理解