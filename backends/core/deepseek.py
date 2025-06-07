from openai import OpenAI
from datetime import datetime, timedelta
import json
from textwrap import dedent
from config.config import Config

cfg = Config()

client = OpenAI(api_key=cfg.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def init_ai(ai_type="schedule_parser", existing_schedules=None):
    """
    初始化AI角色设定和能力
    :param ai_type: AI类型，目前支持'schedule_parser'(日程解析)和其他类型
    :param existing_schedules: 已有日程列表，用于冲突检查
    :return: 包含系统提示词的字典
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 基础角色设定
    base_prompt = {
        "role": "你是一个多功能AI助手，能够处理多种大学生学习和生活相关任务",
        "capabilities": [
            "自然语言理解和生成",
            "时间日期解析和计算",
            "结构化数据生成",
            "任务优先级评估"
        ],
        "knowledge": {
            "academic": "了解大学生常见课程、作业和考试安排",
            "time_management": "熟悉时间管理和日程规划原则",
            "reminder_rules": "掌握提醒事项设置的最佳实践"
        }
    }
    
    # 已有日程文本
    existing_schedules_text = ""
    if existing_schedules:
        existing_schedules_text = dedent(f"""
            ## 已有日程\n当前已有日程如下：
            ```json\n{json.dumps(existing_schedules, indent=2, ensure_ascii=False)}\n```
        """).strip()

    # 根据不同类型返回特定的系统提示词
    if ai_type == "schedule_parser":
        return {
            "system_prompt": dedent(f"""
                # 角色设定
                {base_prompt['role']}，特别擅长日程和提醒事项的解析与生成。

                ## 专项能力
                1. 类型判断：准确区分日程(Schedule)和提醒事项(Reminder)
                2. 信息提取：从文本中提取关键信息（时间、内容、优先级等）
                3. 冲突检测：检查新事项与已有日程的时间冲突
                4. 时间推算：根据模糊时间描述计算具体时间点

                ## 日程解析专项知识
                - 理论作业通常耗时2-6小时
                - 实验报告通常耗时4-10小时
                - 课程复习通常需要3-8小时/科目
                - 能解析自然语言时间描述（如"下周三""三天后"）

                ## 输出格式要求
                请根据输入内容判断是日程还是提醒事项，并返回对应JSON格式：

                ### 日程(Schedule)格式：
                {{
                    "type": "schedule",
                    "content": {{
                        "title": "日程标题",
                        "content": "详细内容",
                        "begin_time": ["YYYY-MM-DD", "HH:MM"],
                        "end_time": ["YYYY-MM-DD", "HH:MM"],
                        "estimated_duration": 预计小时数,
                        "conflict_check": "冲突提示(如有)"
                    }}
                }}

                ### 提醒事项(Reminder)格式：
                {{
                    "type": "reminder",
                    "content": {{
                        "title": "提醒标题",
                        "content": "提醒内容",
                        "end_time": ["YYYY-MM-DD", "HH:MM"],
                        "conflict_check": "冲突提示(如有)"
                    }}
                }}

                ## 已有日程
                {existing_schedules_text}

                ## 当前日期
                今天是{today}
            """).strip()
        }
    else:
        # 其他AI类型的初始化可以在这里扩展
        return {
            "system_prompt": dedent(f"""
                # 通用AI助手
                {base_prompt['role']}，可以处理各种学习和生活相关问题。

                ## 通用能力
                - 回答问题
                - 提供建议
                - 简单计算
                - 信息查询

                ## 当前日期
                今天是{today}
            """).strip()
        }

def parse_schedule(content, existing_schedules=None):
    """解析日程/提醒事项专用函数"""
    # 初始化AI
    ai_config = init_ai("schedule_parser", existing_schedules)
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": ai_config["system_prompt"]},
            {"role": "user", "content": content}
        ],
        response_format={"type": "json_object"},
        stream=False
    )

    if response.choices[0].message.content is None:
        raise ValueError("Response content is None and cannot be parsed as JSON.")
    
    ai_response = json.loads(response.choices[0].message.content)
    item_type = ai_response.get("type", "schedule")  # 默认为schedule

    # 定义默认模板
    DEFAULT_TEMPLATES = {
        "schedule": {
            "id": None,
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
                "remind_before": 60,
                "estimated_duration": 0,
                "conflict_check": "",
                "tag": "学习",
                "additional_info": [],
                "archive": False,
                "archive_time": ""
            }
        },
        "reminder": {
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
                "tag": "提醒",
                "additional_info": [],
                "archive": False,
                "archive_time": ""
            }
        }
    }

    # 选择对应类型的模板
    template = DEFAULT_TEMPLATES[item_type].copy()
    
    # 递归更新嵌套字典
    def update_dict(original, updates):
        for key, value in updates.items():
            if isinstance(value, dict) and key in original:
                update_dict(original[key], value)
            else:
                original[key] = value
    
    update_dict(template, ai_response)
    
    return template

def ask_ai(question):
    """通用问答函数"""
    ai_config = init_ai("general")
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": ai_config["system_prompt"]},
            {"role": "user", "content": question}
        ],
        stream=False
    )
    
    return response.choices[0].message.content

def determine_ai_type(user_input):
    """
    让AI自动判断输入内容的类型，返回对应的处理类型
    :param user_input: 用户输入文本
    :return: ai_type (schedule_parser|general)
    """
    # 系统提示词让AI自己判断类型
    system_prompt = dedent("""
        请根据用户输入内容判断最适合的处理类型：
        1. 如果包含任务、作业、会议等有时间要求的活动 → schedule_parser
        2. 如果只是简单提醒(如"记得买书") → schedule_parser
        3. 如果是普通问题或聊天 → general
        
        只需返回JSON格式：
        {"ai_type": "schedule_parser|general"}
    """)
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        response_format={"type": "json_object"},
        stream=False
    )
    
    result = json.loads(response.choices[0].message.content)
    return result["ai_type"]

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