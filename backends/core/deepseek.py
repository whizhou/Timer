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
        - 冲突检查：检查新生成的日程的持续周期内是否与已有日程的持续时间冲突，如果有冲突，则给出冲突提示（如规划时间的建议，"期间有其他日程，如xx日程（日程时间）等，建议合理规划时间"）

        ## 知识储备
        - 理论课程作业通常耗时：2-6小时
        - 实验及实验报告通常耗时：4-10小时
        - 常见自然语言时间解析（如“下周三”“三天后”）
        - 大学生常见学术时间管理经验

        ## 处理规则
        1. 若输入中包含明确时间（如"5月10日前"）则直接采用；
        2. 若输入为模糊时间（如"下周三"），根据当前日期 {today} 自动推算具体截止时间；
        3. 生成标题格式：[动作] + [对象]，如"完成微积分理论作业"；
        4. 耗时估算标准：
        - 理论作业（2-6小时）
        - 实验操作（3-6小时）
        - 实验报告撰写（2-4小时）
        5. 计算合理的最晚开始时间，预留充足完成时间；
        6. 输出要求为**标准合法JSON格式**，包括以下字段：
        ```json
        {{
        "title": "生成的日程标题",
        "content": "用户输入的完整任务内容（必要时稍作整理）",
        "deadline": "YYYY-MM-DD",
        "estimated_duration": "预计耗时（小时数）",
        "recommended_slots": ["推荐的开始时间（YYYY-MM-DD）"],
        "conflict_check": "冲突提示（如有冲突）"
        }}
        ```

        {existing_schedules_text}
    """).strip()

    # print(f"Sytem Prompt:\n{system_prompt}")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ],
        response_format={"type": "json_object"},
        stream=False
    )

    result = json.loads(response.choices[0].message.content)
    # deadline = datetime.strptime(result["deadline"], "%Y-%m-%d")
    # result["daily_reminder_start"] = (deadline - timedelta(days=3)).strftime("%Y-%m-%d")  # 截止前3天开始每日提醒
    
    return result

existing_schedules = [
    {
        "title": "完成概率论理论作业",
        "deadline": "2025-05-10",
        "estimated_duration": 4,
        "recommended_slots": ["2025-05-08", "2025-05-09"]
    },
    {
        "title": "撰写线性代数实验报告",
        "deadline": "2025-05-12",
        "estimated_duration": 6,
        "recommended_slots": ["2025-05-09", "2025-05-10"]
    }
]

input_text = "创建数值分析作业\n"
input_text += dedent("""
    @所有人 同学们，本周作业是：教材第135-136页"习题"，题 1 (2), (3), (4)；2 (3)；3；4；5；7; 8 (1)。下周三交作业。
    """).strip()

print(f"\n\nInput Text:\n{input_text}")

schedule = parse_schedule(input_text, existing_schedules=existing_schedules)

print(f"\n\n\nGenerated Schedule:")
print(json.dumps(schedule, indent=2, ensure_ascii=False))
print("\n\n\n")