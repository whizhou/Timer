from openai import OpenAI
from datetime import datetime, timedelta
import json
from textwrap import dedent
from ..config.config import Config

cfg = Config()

client = OpenAI(api_key=cfg.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def parse_schedule(content, existing_schedules=None):
    # 系统提示词需要明确结构化输出要求

    today = datetime.now().strftime("%Y-%m-%d")  # 获取当前日期

    existing_schedules_text = ""
    if existing_schedules:
        existing_schedules_text = dedent(f"""
            ## 已有日程\n当前已有日程如下，请合理安排时间，尽量避免与下列任务冲突：
            ```json\n{json.dumps(existing_schedules, indent=2, ensure_ascii=False)}\n```
        """).strip()

    system_prompt = dedent(f"""
        # 角色设定
        你是一个专业的大学生日程生成助手，擅长从学生输入的任务中提取关键信息（如截止时间、任务内容），并智能推断合理的日程标题、主要内容、预计耗时、最晚开始时间。

        ## 能力
        - 信息提取：精准识别截止时间、任务描述等关键字段
        - 智能推断：根据任务类型生成简洁明了的日程标题（如"XX课程理论作业"、"XX课程实验报告"）
        - 时间估算：结合常见作业、实验难度推算合理完成时间
        - 日程简化：提取最重要的任务信息，不删除任何关键信息
        - 结构化输出：统一以标准JSON格式输出日程信息
        - 冲突检查：检查新生成的日程的持续周期内是否与已有日程的持续时间重叠，持续时间定义为推荐的最晚开始时间到截止时间之间的时间段（如"2025-05-08"到"2025-05-10"），
            如果有重叠，则给出冲突提示（如规划时间的建议，"期间有其他日程，如xx日程（日程时间）等，建议合理规划时间"）

        ## 知识储备
        - 理论课程作业通常耗时：2-6小时
        - 实验及实验报告通常耗时：4-10小时
        - 常见自然语言时间解析（如"下周三""三天后"）
        - 大学生常见学术时间管理经验

        ## 处理规则
        0. 首先判断用户输入内容应生成哪种类型（schedule 或 reminder），再严格按照对应的JSON格式生成输出。
            判断规则为有具体的起止时间或明确说明是日程是schedule，否则为reminder。
            - 例如：“提醒我明天交作业”应为reminder；
            - “5月10日14:00-16:00参加会议”应为schedule。
        1. 若输入中包含明确时间（如"5月10日前"）则直接采用；
        2. 若输入为模糊时间（如"下周三"），根据当前日期 {today} 自动推算具体截止时间；
        3. 生成标题格式：[动作] + [对象]，如"完成微积分理论作业"；
        4. 耗时估算标准：
        - 理论作业（2-6小时）
        - 实验操作（3-6小时）
        - 实验报告撰写（2-4小时）
        5. 计算合理的最晚开始时间，预留充足完成时间；
        6. 你只需要返回需要修改的字段，其他字段将使用默认值。输出要求为**标准合法JSON格式**，包括以下字段（只需返回需要修改的字段）：
        
        ### 日程(schedule)格式：
        ```json
        {{
            "type": "schedule",
            "title": "生成的日程标题",
            "content": "用户输入的完整任务内容",
            "begin_time": ["YYYY-MM-DD", "HH:MM"],
            "end_time": ["YYYY-MM-DD", "HH:MM"],
            "remind_start": ["YYYY-MM-DD", "HH:MM"],
            "estimated_duration": "预计耗时（小时数）",
            "conflict_check": "冲突提示（如有冲突）",
            "additional_info": ["任何额外信息"]
        }}
        ```

        ### 提醒事项(reminder)格式：
        ```json
        {{
            "type": "reminder",
            "title": "提醒标题",
            "content": "提醒内容",
            "end_time": ["YYYY-MM-DD", "HH:MM"],
            "remind_start": ["YYYY-MM-DD", "HH:MM"],
            "remind_before": "提前提醒时间(分钟)",
            "conflict_check": "冲突提示",
            "additional_info": ["额外信息"]
        }}
        ```
        ## 已有日程
        {existing_schedules_text}

        ## 特别注意
        1. 必须明确返回"type"字段指明是schedule还是reminder
        2. 你只需要返回需要修改的字段，其他字段将使用默认值。例如，如果你只需要修改标题和内容，可以只返回：
        {{
            "title": "新标题",
            "content": "新内容"
        }}
        3. 其他字段将使用默认值
        4. 如果用户输入没有明确的起止时间，仅为提醒事项，请务必输出"type": "reminder"
    """).strip()

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ],
        response_format={"type": "json_object"},
        stream=False
    )

    if response.choices[0].message.content is None:
        raise ValueError("Response content is None and cannot be parsed as JSON.")
    
    ai_response = json.loads(response.choices[0].message.content)

    # 定义默认日程模板
    DEFAULT_SCHEDULE_TEMPLATE = {
        "id": None,  # 将由数据库分配
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "schedule",
        "AI_readable": True,
        "content": {
            "title": "",
            "content": "",
            "whole_day": False,
            "begin_time": ["", "08:00"],
            "end_time": ["", "23:59"],
            "location": "",
            "remind_start": ["", "08:00"],
            "remind_before": 60,  # 默认提前60分钟提醒
            "estimated_duration": 0,
            "conflict_check": "",
            "tag": "学习",  # 默认标签
            "repeat": {
                "repeat": False,
                "type": "",
                "every": 1,
                "repeat_until": ["", "23:59"]
            },
            "additional_info": [],
            "archive": False,
            "archive_time": ""
        }
    }

    # 新增：定义默认提醒模板
    DEFAULT_REMINDER_TEMPLATE = {
        "id": None,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "reminder",
        "AI_readable": True,
        "content": {
            "title": "",
            "content": "",
            "end_time": ["", "23:59"],
            "remind_start": ["", "08:00"],
            "remind_before": 60,
            "conflict_check": "",
            "tag": "",
            "additional_info": [],
            "archive": False,
            "archive_time": ""
        }
    }
    
    # 根据AI返回的type选择模板
    ai_type = ai_response.get("type", "schedule")
    if ai_type == "reminder":
        target_json = DEFAULT_REMINDER_TEMPLATE.copy()
    else:
        target_json = DEFAULT_SCHEDULE_TEMPLATE.copy()

    # 递归更新嵌套字典，仅更新被AI识别到的字段
    def update_dict(original, updates):
        for key, value in updates.items():
            if isinstance(original, dict) and key in original:
                if isinstance(value, dict) and isinstance(original[key], dict):
                    update_dict(original[key], value)
                else:
                    original[key] = value

    # 只更新content字段内被识别到的项
    update_dict(target_json["content"], ai_response)

    return target_json

# 测试数据
existing_schedules = [
    {
        "id": "schedule_001",
        "timestamp": "2025-05-01 10:00:00",
        "type": "schedule",
        "AI_readable": True,
        "content": {
            "title": "完成概率论理论作业",
            "content": "教材第50-52页习题",
            "whole_day": False,
            "begin_time": ["2025-05-08", "14:00"],
            "end_time": ["2025-05-08", "18:00"],
            "remind_start": ["2025-05-07", "08:00"],
            "remind_before": 60,
            "estimated_duration": 4,
            "tag": "学习"
        }
    },
    {
        "id": "schedule_002",
        "timestamp": "2025-05-02 15:30:00",
        "type": "schedule",
        "AI_readable": True,
        "content": {
            "title": "撰写线性代数实验报告",
            "whole_day": False,
            "begin_time": ["2025-05-09", "19:00"],
            "end_time": ["2025-05-09", "23:00"],
            "remind_start": ["2025-05-08", "08:00"],
            "estimated_duration": 4,
            "tag": "学习"
        }
    }
]

input_text = "创建数值分析作业\n"
input_text += dedent("""
    @所有人 同学们，本周作业是：教材第136页的"习题"中的题 10；18；以及教材第175-176页的"习题"中的 题 1；7 。下周三交作业。
    """).strip()

print(f"\n\nInput Text:\n{input_text}")

schedule = parse_schedule(input_text, existing_schedules=existing_schedules)

print(f"\n\n\nGenerated Schedule:")
print(json.dumps(schedule, indent=2, ensure_ascii=False))
print("\n\n\n")