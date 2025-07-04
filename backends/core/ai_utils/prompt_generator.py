from datetime import datetime, timedelta
import json
from textwrap import dedent
from typing import Dict, Optional, List

    
class PromptGenerator:
    """提示词生成器，专注于为日程管理生成各类系统提示词"""

    def _generate_analyse_prompt(
        cls, 
        existing_schedules: Optional[List[Dict]] = None
    ) -> str:
        """生成语义分析提示词"""
        existing_schedules_text = ""
        if existing_schedules:
            existing_schedules_text = dedent(f"""
                ## 已有日程\n当前已有日程如下：
                ```json\n{json.dumps(existing_schedules, indent=2, ensure_ascii=False)}\n```
            """).strip()

        today = datetime.now().strftime("%Y-%m-%d")

        return dedent(f"""
            ## 已有日程
            {existing_schedules_text}

            ## 当前日期
            {today}
            ## 任务说明
            你是一个专业的面向大学生的意图分类器，只需分析用户的最新输入，判断其意图类型。

            ## 意图类型定义（严格选择一项，优先考虑CREATE/MODIFY/DELETE/INQUIRY，只有完全无法归类时才选GENERAL）：
            1. CREATE - 用户明确表示要"添加"、"新建"、"安排"、"创建"日程，或描述未来某时间要做的事
            - 包括以老师的口吻布置作业、考试、任务、活动等，且需要包含一个明确时间点，也应判定为CREATE
            2. MODIFY - 用户使用"修改"、"调整"、"更新"、"改为"、"换成"等动词，或提到已有日程的变更
            - 在添加、删减内容但是没有指代词且缺少时间时，应该与上文对应项比对，若内容符合更改则判定为MODIFY
            3. DELETE - 用户使用"删除"、"取消"、"移除"等动词，或表示不再需要某日程
            4. INQUIRY - 用户使用"查询"、"查看"、"有哪些"等词询问日程信息
            5. GENERAL - 仅当用户输入完全无法归类为上述四类时才选择GENERAL。GENERAL仅用于以下情况：
            - 明显的闲聊、问候、无关日程的内容（如“你好”“你是谁”“天气怎么样”）
            - 用户输入与日程、提醒、查询、修改、删除均无关，且无法推断出任何日程相关意图
            - 不要因为模型不确定而选择GENERAL，优先尝试归类为CREATE/MODIFY/DELETE/INQUIRY

            ## 分析规则
            1. 主要关注当前输入
            2. 当前输入包含指代词（如"刚才的安排"）时，关注当前输入的动词。
            3. 当前输入与上文用户输入时间结点或主体重合时，要关注是否是对上文的更改。
            4. 如果语句中包含多个意图，选择最核心的意图
            5. 只需返回大写关键词（CREATE/MODIFY/DELETE/INQUIRY/GENERAL）
            6. 不要添加任何解释或额外文本
            7. 除非完全无法归类，否则不要选择GENERAL

            ## 指代解析指南
            - "这个" → 最近提到的日程
            - "刚才的" → 最近一次操作
            - "之前的" → 最近的历史操作（倒数第二个）

            ## 示例
            历史1: "创建明天下午3点的会议"
            当前: "删除这个" → DELETE

            历史1: "创建明天下午3点的会议"
            当前: "把明天下午3点的会议改为明天上午10点" → MODIFY

            历史1: "查看下周会议"
            历史2: "把周二的改到周三"
            当前: "取消刚才的安排" → DELETE

            当前: "你好" → GENERAL
            当前: "你是谁" → GENERAL
            当前: "帮我查一下明天的安排" → INQUIRY
            当前: "安排明天下午两点的讨论" → CREATE
        """).strip()

    def _generate_system_prompt(
        cls, 
        existing_schedules: Optional[List[Dict]] = None
    ) -> str:
        """生成系统提示词"""
        existing_schedules_text = ""
        if existing_schedules:
            existing_schedules_text = dedent(f"""
                ## 已有日程\n当前已有日程如下：
                ```json\n{json.dumps(existing_schedules, indent=2, ensure_ascii=False)}\n```
            """).strip()

        today = datetime.now().strftime("%Y-%m-%d")

        return dedent(f"""
            # 角色设定
            你是一个专业的大学生日程生成助手，擅长从学生输入的任务中提取关键信息。

            ## 处理规则
            1. 首先判断是schedule还是reminder类型
            2. 只返回需要修改的字段
            3. 必须包含type字段

            ## 已有日程
            {existing_schedules_text}

            ## 当前日期
            {today}
        """).strip()
    
    def _generate_template_json(self) -> str:
        """生成默认日程/提醒的JSON模板描述"""
        template = dedent("""
            ## JSON格式模板
            
            日程(schedule)和提醒(reminder)的标准格式如下：
            
            ### 日程(schedule)模板
            ```json
            {
                "id": "日程ID",默认设置为-1
                "timestamp": "最后修改时间(YYYY-MM-DD HH:MM:SS)",
                "type": "schedule",
                "AI_readable": true/false,默认设置为true
                "content": {
                    "title": "日程标题",
                    "content": "详细内容(可选)",
                    "whole_day": true/false,默认设置为false
                    "begin_time": ["YYYY-MM-DD", "HH:MM:SS (默认08:00:00)"],
                    "end_time": ["YYYY-MM-DD", "HH:MM:SS (默认23:59:59)"],
                    "location": "地点(可选)",
                    "remind_start": ["YYYY-MM-DD", "HH:MM:SS (默认08:00:00)"],
                    "remind_before": "提前提醒分钟数(可选)"（默认设置为120）
                    "tag": "标签(可选)",默认设置为default
                    "repeat": {
                        "repeat": true/false,默认设置为false
                        "type": "重复类型(daily/weekly/monthly)(可选)",
                        "every": "重复间隔(可选)",
                        "repeat_until": ["YYYY-MM-DD", "HH:MM:SS (默认23:59:59)"]
                    },
                    "additional_info": [
                        "附加信息(可选)"，默认设置为空
                    ],
                    "archive": true/false,默认设置为false
                    "archive_time": "归档时间(YYYY-MM-DD HH:MM:SS)"
                }
            }
            ```
            
            ### 提醒(reminder)模板
            ```json
            {
                "id": "提醒ID",默认设置为-1
                "timestamp": "最后修改时间(YYYY-MM-DD HH:MM:SS)",
                "type": "reminder",
                "AI_readable": true/false,默认设置为true
                "content": {
                    "title": "提醒标题",
                    "content": "详细内容(可选)",
                    "end_time": ["YYYY-MM-DD", "HH:MM:SS (默认23:59:59)"],
                    "remind_start": ["YYYY-MM-DD", "HH:MM:SS (默认08:00:00)"],
                    "remind_before": "提前提醒分钟数(可选)",（默认设置为120）
                    "conflict_check": "冲突检查信息(可选)",默认设置为false
                    "tag": "标签(可选)",默认设置为default
                    "additional_info": [
                        "附加信息(可选)"，默认设置为空
                    ],
                    "archive": true/false,默认设置为false
                    "archive_time": "归档时间(YYYY-MM-DD HH:MM:SS)"
                }
            }
            ```
        """).strip()
        return template

    def _parse_creation(
        self,
        existing_schedules: Optional[List[Dict]] = None
    ) -> str:
        """生成创建日程/提醒的专用提示词"""
        base_prompt = self._generate_system_prompt(existing_schedules)
        template_json = self._generate_template_json()
        
        creation_rules = dedent("""
            ## 创建规则
            1. 从用户输入中提取字段，遵循以下模板格式，没有识别到的非必填字段不添加进返回的dict中:
            
            {template_json}
            
            2. 必填字段和不必说明:
            - 对于reminder类型:
                * 当缺少明确的begin_time和end_time时，自动设置为reminder类型
                * 仅有一个时间点（如“下午三点”或“明天三点”）时，自动设置为reminder类型
                * content中的title, end_time为必填项
                * remind_start和remind_before为必填项(默认值分别为end_time那一天的08:00:00和120分钟)
            - 对于schedule类型:
                * 必须同时有明确的begin_time和end_time，只有其中一项无法设置为schedule类型。
                * 只有用户输入中同时包含起始时间(begin_time)和结束时间(end_time)时，才可设置为schedule类型，否则一律为reminder类型
                * content中的title, begin_time, end_time为必填项
                * remind_start和remind_before为必填项(默认值分别为end_time那一天的08:00:00和120分钟)
            
             3. 特别注意:
            - 完全忽略id字段的识别和创建，id应由数据库自动生成
            - 所有id字段应保持为None或直接不包含该字段
            
            4. 时间处理规则:
            - 如果用户只说"今天"，使用当前日期
            - 如果只说时间没有日期，假定为当前日期
            - 模糊时间表述要转化为具体时间
            
            5. 示例响应:
            ### schedule示例:
            ```json
            {{
                "type": "schedule",
                "content": {{
                    "title": "小组会议",
                    "begin_time": ["2023-10-15", "14:00:00"],
                    "end_time": ["2023-10-15", "15:30:00"],
                    "remind_start": ["2023-10-15", "08:00:00"],
                    "remind_before": 120,
                }}
            }}
            ```
            
            ### reminder示例:
            ```json
            {{
                "type": "reminder",
                "content": {{
                    "title": "提交作业",
                    "content": "记得提交数学作业"
                    "end_time": ["2023-10-16", "23:59:59"],
                    "remind_start": ["2023-10-16", "08:00:00"],
                    "remind_before": 120,
                }}
            }}
            ```
            
            6. 只返回JSON格式结果，不要解释
        """).strip().format(template_json=template_json)
    
        return f"{base_prompt}\n\n{creation_rules}"

    def _parse_modification(
            self,
            existing_schedules: Optional[List[Dict]] = None
        ) -> str:
            """生成修改日程的专用提示词"""
            if not existing_schedules:
                raise ValueError("修改日程必须提供已有日程列表")
                
            base_prompt = self._generate_system_prompt(existing_schedules)
            
            modification_rules = dedent("""
                ## 修改规则
                1. 首先精确识别用户要修改哪个日程:
                - 匹配日程的id字段(最高优先级)
                - 如果没有明确id，则按以下顺序匹配:
                    1) 匹配标题中的关键词(必须包含完整关键词)
                    2) 匹配具体的时间范围(日期+时间必须完全匹配)
                    3) 匹配内容中的关键词
                - 如果匹配多个，返回最接近当前时间的一个
                
                2. 响应必须包含三个部分:
                - id: 被修改日程的id
                - original: 原始完整日程内容
                - modified: 修改后完整的日程内容
                
                3. 字段处理规则:
                - 必须始终包含id字段
                - 修改时间时，必须自动调整相关提醒时间，重新计算remind_start和remind_before
                    (默认值分别为修改后的end_time那一天的08:00:00和120分钟)
                - 只有明确提出修改为日程，并且给出了schedule所需的begin_time才会修改为schedule
                - 如果是在原字段上添加内容的话，应该保留源字段的前提下加上新的部分
                - 如果是在原字段上减少部分内容的话，应该保留未减少的原字段部分
                - 无论什么条件下，返回的两个日程必须是完整的，符合json模版要求的
                
                
                4. 示例响应:
                ### 修改示例:
                ```json
                {
                    "schedule_id": "schedule_123",
                    "original": {
                        "id": "schedule_123",
                        "timestamp": "2023-10-14 10:00:00",
                        "type": "schedule",
                        "AI_readable": true,
                        "content": {
                            "title": "小组会议",
                            "content": "讨论项目进度",
                            "whole_day": false,
                            "begin_time": ["2023-10-15", "14:00:00"],
                            "end_time": ["2023-10-15", "15:00:00"],
                            "location": "会议室A",
                            "remind_start": ["2023-10-15", "08:00:00"],
                            "remind_before": 120,
                            "tag": "work",
                            "repeat": {
                                "repeat": false
                            },
                            "additional_info": [],
                            "archive": false
                        }
                    },
                    "modified": {
                        "id": "schedule_123",
                        "timestamp": "2023-10-14 11:30:00",  # 更新时间戳
                        "type": "schedule",
                        "AI_readable": true,
                        "content": {
                            "title": "项目进度会议",  # 修改标题
                            "content": "讨论项目进度",
                            "whole_day": false,
                            "begin_time": ["2023-10-15", "14:30:00"],  # 修改开始时间
                            "end_time": ["2023-10-15", "15:30:00"],   # 修改结束时间
                            "location": "会议室A",
                            "remind_start": ["2023-10-15", "08:00:00"],
                            "remind_before": 120,
                            "tag": "work",
                            "repeat": {
                                "repeat": false
                            },
                            "additional_info": [],
                            "archive": false
                        }
                    }
                }
                ```
            """).strip()
            
            return f"{base_prompt}\n\n{modification_rules}"

    def _parse_delete(
        self,
        existing_schedules: Optional[List[Dict]] = None
    ) -> str:
        """生成删除日程的专用提示词"""
        if not existing_schedules:
            raise ValueError("删除日程必须提供已有日程列表")
            
        base_prompt = self._generate_system_prompt(existing_schedules)
        
        delete_rules = dedent("""
            ## 删除规则
            1. 你的任务是根据用户输入，在已有日程列表中查找最匹配的日程，并返回其id和title。
            2. 匹配优先级如下（按顺序）：
                a. id完全匹配（如用户直接说“删除id为X的日程”）
                b. content中的title完全匹配（如“删除‘XXX’日程”）
                c. content中的title部分匹配（如“上一个日程”“刚才的日程”“取消人工智能考试”）
                d. 时间完全匹配（如“删除明天8点的日程”）
                e. content中的content部分匹配（如“删除交作业的提醒”）
                f. 如果用户说“上一个日程”“刚才的日程”，请选取时间最接近当前时间且未归档的日程。
            3. id和title必须严格从已有日程列表中选取，不能凭空生成。
            4. 如果找不到任何匹配项，返回空对象：`{}`。
            5. 返回格式如下：
            ```json
            {
                    "id": 1,
                    "title": "完成数值分析作业"
            }
            ```
            6. 只返回JSON格式结果，不要解释。
        """).strip()
        
        return f"{base_prompt}\n\n{delete_rules}"
    
    def _parse_inquiry(
        self,
        existing_schedules: Optional[List[Dict]] = None
    ) -> str:
        """生成查询日程的专用提示词"""
        if not existing_schedules:
            raise ValueError("查询日程必须提供已有日程列表")
            
        base_prompt = self._generate_system_prompt(existing_schedules)
        
        inquiry_rules = dedent("""
            ## 查询规则
            0. 如果用户没有说明任何查询条件，默认返回时间最近的至多3个未归档日程。
            1. 否则你的任务是根据用户输入，在已有日程列表中查找匹配度比较高的日程，并返回匹配日程的完整日志json。
            2. 匹配优先级如下（按顺序）：
                a. 时间范围匹配（如“查询明天的日程”）
                b. 标题完全匹配（如“查询‘XXX’日程”）
                c. 标题部分匹配（如“上一个日程”“刚才的日程”“查询人工智能考试”）
                d. 内容部分匹配（如“查询交作业的提醒”）
                e. id完全匹配（如用户直接说“查询id为X的日程”）
                f. 如果用户说“上一个日程”“刚才的日程”，请选取时间最接近当前时间且未归档的日程。
            3. 返回的完整日程项必须严格从已有日程列表中选取，不能凭空生成。
            4. 返回格式如下：
            ```json
            {
                "schedule_list": [
                     {
                        "id": "123",
                        "timestamp": "2025-06-19 10:00:00",
                        "type": "schedule",
                        "AI_readable": true,
                        "content": {
                            "title": "小组会议",
                            "content": "讨论项目进度",
                            "whole_day": false,
                            "begin_time": ["2023-10-15", "14:00:00"],
                            "end_time": ["2023-10-15", "15:00:00"],
                            "location": "会议室A",
                            "remind_start": ["2023-10-15", "08:00:00"],
                            "remind_before": 120,
                            "tag": "work",
                            "repeat": {
                                "repeat": false
                            },
                            "additional_info": [],
                            "archive": false
                        }
                    },
                    {
                        "id": "234",
                        "timestamp": "2024-10-16 10:00:00",
                        "type": "schedule",
                        "AI_readable": true,
                        "content": {
                            "title": "数值分析作业",
                            "content": "",
                            "whole_day": false,
                            "begin_time": ["2024-10-19", "08:00:00"],
                            "end_time": ["2024-10-19", "20:00:00"],
                            "location": "",
                            "remind_start": ["2024-10-19", "08:00:00"],
                            "remind_before": 120,
                            "tag": "default",
                            "repeat": {
                                "repeat": false
                            },
                            "additional_info": [],
                            "archive": false
                        }
                    },
                ]
            }
            ```
            5. 只返回JSON格式结果，不要解释。
        """).strip()
        
        return f"{base_prompt}\n\n{inquiry_rules}"
    
    def _generate_general_prompt(self) -> str:
        general_prompt = dedent(f"""
            你是一个智能助手，对于用户输入，请直接给出回复内容，不要包含其他说明。
                                
            请用友好、专业的语气回复以下用户输入：
        """).strip()
        return f"{general_prompt}"

