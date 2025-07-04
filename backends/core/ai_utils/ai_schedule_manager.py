from openai import OpenAI
import json
import re
from textwrap import dedent
from config.config import Config
from typing import Dict, Union, Optional, List
from copy import deepcopy

class AIScheduleManager:
    """AI日程管理器，负责处理用户输入的语义分析并生成对应的日程管理响应"""
    def __init__(self):
        cfg = Config()
        self.client = OpenAI(api_key=cfg.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        
        # 默认日程模板
        self.DEFAULT_SCHEDULE_TEMPLATE = {
            "id": -1,
            "timestamp": None,  # 将在创建时填充
            "type": "schedule",
            "AI_readable": True,
            "content": {
                "title": "",
                "content": "",
                "whole_day": False,
                "begin_time": ["", "08:00:00"],  # 日期将在创建时填充
                "end_time": ["", "23:59:59"],    # 日期将在创建时填充
                "location": "",
                "remind_start": ["", "08:00:00"],  # 将根据end_time自动计算
                "remind_before": 120,  # 默认120分钟(2小时)
                "tag": "default",
                "repeat": {
                    "repeat": False,
                    "type": "",  # daily/weekly/monthly
                    "every": 1,  # 重复间隔
                    "repeat_until": ["", "23:59:59"]
                },
                "additional_info": [],
                "archive": False,
                "archive_time": ""
            }
        }
        
        # 默认提醒模板
        self.DEFAULT_REMINDER_TEMPLATE = {
            "id": -1,
            "timestamp": None,  # 将在创建时填充
            "type": "reminder",
            "AI_readable": True,
            "content": {
                "title": "",
                "content": "",
                "end_time": ["", "23:59:59"],  # 日期将在创建时填充
                "remind_start": ["", "08:00:00"],  # 将根据end_time自动计算
                "remind_before": 120,  # 默认120分钟(2小时)
                "conflict_check": False,
                "tag": "default",
                "additional_info": [],
                "archive": False,
                "archive_time": ""
            }
        }

    def _analyze_semantic_intent(self, prompt_content: List[Dict[str, str]]) -> str:
        """分析用户输入的隐含意图"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=prompt_content,
                temperature=0.3,
                max_tokens=16
            )
            
            result = response.choices[0].message.content.strip().upper()
            return result if result in ["CREATE", "MODIFY", "DELETE", "INQUIRY"] else "GENERAL"
        except Exception as e:
            print(f"语义分析出错: {e}")
            return "GENERAL"

    def _handle_creation_response(self, prompt_content: List[Dict[str, str]]) -> Dict:
        """
        处理创建日程/提醒的响应（内部方法）
        逻辑：先识别type，再选择模板，最后递归更新字段
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=prompt_content,
                temperature=0.3,
                max_tokens=1024,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            raw_data = self._extract_json(content)
            
            # 1. 确定类型并选择模板
            schedule_type = raw_data.get("type", "")
            if schedule_type == "schedule":
                result = deepcopy(self.DEFAULT_SCHEDULE_TEMPLATE)
            elif schedule_type == "reminder":
                result = deepcopy(self.DEFAULT_REMINDER_TEMPLATE)
            else:
                return {"error": "无法识别的类型"}
            
            # 2. 递归更新字段
            self._recursive_update(result, raw_data)
            return result
            
        except Exception as e:
            return {"error": str(e)}

    def _handle_modification_response(self, prompt_content: List[Dict[str, str]]) -> Dict[str, Dict]:
        """
        处理修改日程的响应（内部方法）
        返回格式：{
            "original": {原始数据},  # 保持API返回的原始结构
            "modified": {修改后数据},  # 保持API返回的修改结构
            "type": "schedule/reminder"  # 从响应中提取的类型
        }
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=prompt_content,
                temperature=0.3,
                max_tokens=1024,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            raw_data = self._extract_json(content)
            
            # 基础验证
            if not isinstance(raw_data, dict):
                return {"error": "响应格式无效"}
            
            # 提取核心字段
            result = {
                "original": raw_data.get("original", {}),
                "modified": raw_data.get("modified", {})
            }
            
            return result
            
        except Exception as e:
            return {"error": str(e)}

    def _handle_deletion_response(self, prompt_content: List[Dict[str, str]]) -> Dict[str, Union[str, int]]:
        """
        处理删除日程的响应（内部方法）
        返回格式：{
            "id": 要删除的日程ID,  # 必须字段
            "title": "要删除的日程标题"  # 必须字段
        }
        或错误格式：{"error": "错误信息"}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=prompt_content,
                temperature=0.3,
                max_tokens=512,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            raw_data = self._extract_json(content)
            
            # 基础验证
            if not isinstance(raw_data, dict):
                return {"error": "响应格式无效"}
            
            # 构建返回结构（严格匹配您要求的格式）
            result = {
                "id": raw_data.get("id"),
                "title": raw_data.get("title", "")
            }
                
            # 验证必须字段
            if result["id"] is None or not result["title"]:
                missing = []
                if result["id"] is None: missing.append("id")
                if not result["title"]: missing.append("title")
                return {"error": f"缺少必要字段: {', '.join(missing)}"}
            
            return result
        
        except Exception as e:
            return {"error": str(e)}
        
        
    def _handle_inquiry_response(self, prompt_content: List[Dict[str, str]]) -> Dict[str, Dict]:
        """
        处理查询日程的响应（内部方法）
        返回格式：{
            "schedule_list" : 查询到的日程列表， # 必须字段
        }
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=prompt_content,
                temperature=0.3,
                max_tokens=2048,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            raw_data = self._extract_json(content)
            
            # 基础验证
            if not isinstance(raw_data, dict):
                return {"error": "响应格式无效"}
            
            # 提取核心字段
            result = {
                "schedule_list": raw_data.get("schedule_list")
            }

             # 验证必须字段
            if result["schedule_list"] is None:
                return {"error": f"缺少必要字段: schedule_list"}
            
            return result
        
        except Exception as e:
            return {"error": str(e)}
        
    def _handle_general_respond(self, prompt_content: List[Dict[str, str]]) -> str:
        """生成对通用意图的正常回复"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=prompt_content,
                temperature=0.7,
                max_tokens=256
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return "我无法处理您的请求，请稍后再试。"

    # 辅助方法 --------------------------------------------------
    
    def _extract_json(self, content: str) -> Dict:
        """从响应内容中提取JSON（不暴露给外部）"""
        try:
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            json_str = json_match.group(1) if json_match else content
            return json.loads(json_str.replace("'", '"'))
        except Exception as e:
            print(f"[JSON解析错误] {e}")
            return {"error": "响应解析失败"}

    def _recursive_update(self, target: Dict, source: Dict):
        """
        递归更新字典字段（不暴露给外部）
        示例：
            target = {"a": 1, "b": {"c": 2}}
            source = {"b": {"c": 3, "d": 4}}
            结果: {"a": 1, "b": {"c": 3, "d": 4}}
        """
        for key, value in source.items():
            if key in target and isinstance(value, dict) and isinstance(target[key], dict):
                self._recursive_update(target[key], value)
            else:
                target[key] = value