# AIScheduler class for managing AI-related tasks and schedules.
# This class is inherited from the Scheduler class and is responsible for managing AI-related tasks and schedules.

import json
import os
import yaml

from typing import List, Dict, Union

from .prompt_generator import PromptGenerator
from .ai_schedule_manager import AIScheduleManager
from .intent_classifier import IntentClassifier
from .scheduler import Scheduler
from .database.schedule_manager import ScheduleManager

class AIScheduler(Scheduler):
    def __init__(self, app=None):
        super().__init__()
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the AIScheduler with the given app."""
        super().init_app(app)
        self.settings = app.config.get('AI_SCHEDULER_SETTINGS', {})
        
        # 初始化依赖组件
        self.prompt_generator = PromptGenerator()
        self.ai_schedule_manager = AIScheduleManager()
        self.intent_classifier = IntentClassifier()
        self.scheduler = Scheduler(app)
        
        # 设置意图处理器
        self._setup_intent_handlers()

    # Add AI-specific methods here

    def _setup_intent_handlers(self):
        """设置意图类型与处理函数的映射关系"""
        self.intent_handlers = {
            "CREATE": self._handle_create_intent,    # 创建意图处理器
            "MODIFY": self._handle_modify_intent,   # 修改意图处理器
            "DELETE": self._handle_delete_intent,    # 删除意图处理器
            "GENERAL": self._handle_general_intent,
        }
    
    def process_user_request(self, user_input: str) -> Union[Dict, str]:
        """
        处理用户输入请求的主入口函数
        
        参数:
            user_input: 用户输入的原始文本
            
        返回:
            如果是特定意图，返回操作结果字典
            如果是通用对话，返回AI生成的响应字符串
        """
        # 第一步：进行意图分类
        intent_result = self.intent_classifier.classify_user_intent(user_input)
        
        # 第二步：根据意图类型获取对应的处理函数
        handler = self.intent_handlers.get(intent_result.intent_type)
        
        return handler(intent_result.original_text)
        # return handler(user_input) # 两者意义相同
    

    def _handle_create_intent(self, user_input: str) -> Dict:
        """处理创建日程/提醒的请求"""
        # 生成创建提示词并获取响应
        all_schedules = self.scheduler.get_schedules()
        prompt = self.prompt_generator._parse_creation(all_schedules)
        creation_result = self.ai_schedule_manager._handle_creation_response(prompt, user_input)
        
        # 错误处理
        if "error" in creation_result:
            return {
                "status": "error",
                "action": "create",
                "message": creation_result["error"]
            }
        
        # 提取创建结果的关键信息
        schedule_type = creation_result.get("type", "")
        content = creation_result.get("content", {})
        title = content.get("title", {})

        created_ids = self.scheduler.create_schedule([creation_result])
        if created_ids and isinstance(created_ids[0], int):
            creation_result['id'] = created_ids[0]
        return {
            "status": "success",
            "action": "create",
            "type": schedule_type,
            "schedule_data": creation_result,  # 完整的创建数据
        }

    def _handle_modify_intent(self, user_input: str) -> Dict:
        """处理修改日程的请求"""
        # 从文本中解析日程ID和修改内容
        all_schedules = self.scheduler.get_schedules()
        prompt = self.prompt_generator._parse_modification(all_schedules)
        modification_result = self.ai_schedule_manager._handle_modification_response(prompt, user_input)

        # 如果处理结果中有错误，返回错误信息
        if "error" in modification_result:
            return {
                "status": "error",
                "message": modification_result["error"]
            }

        # 提取原始和修改后的数据
        original_data = modification_result.get("original", {})
        modified_data = modification_result.get("modified", {})
        
        # 获取日程ID（假设从original或modified中获取）
        schedule_id = original_data.get("id") or modified_data.get("id")
        
        self.scheduler.update_schedule(schedule_id, modified_data)

        return {
            "status": "success",
            "action": "modify",
            "schedule_id": schedule_id,
            "original": original_data,
            "modified": modified_data
        }
    
    def _handle_delete_intent(self, user_input: str) -> Dict:
        """处理删除日程的请求"""
        # 从文本中解析日程ID
        all_schedules = self.scheduler.get_schedules()
        prompt = self.prompt_generator._parse_delete(all_schedules)
        deletion_result = self.ai_schedule_manager._handle_deletion_response(prompt, user_input)
        
        # 如果处理结果中有错误，返回错误信息
        if "error" in deletion_result:
            return {
                "status": "error",
                "action": "delete",
                "message": deletion_result["error"]
            }
        
        # 获取删除的日程信息
        schedule_id = deletion_result.get("id")
        schedule_title = deletion_result.get("title", "")

        self.scheduler.delete_schedule(schedule_id)
        
        return {
            "status": "success",
            "action": "delete",
            "schedule_id": schedule_id,
            "schedule_title": schedule_title
        }
    
    def _handle_general_intent(self, user_input: str) -> Union[Dict ,str]:
        """处理通用意图的回复生成，使用语义分析判断隐含意图"""
        # 使用大语言模型进行语义分析
        semantic_result = self.ai_schedule_manager.analyze_semantic_intent(user_input)
        
        if semantic_result and semantic_result != "GENERAL":
            handler = self.intent_handlers.get(semantic_result)
        
            return handler(user_input)
        
        # 如果语义分析也没有识别出特定意图，返回正常回复
        return self._handle_conservation_intent(user_input)
    
    def _handle_conservation_intent(self, user_input: str) -> str:
        """处理通用对话请求的后备方法"""
        prompt = self.prompt_generator._generate_general_prompt()
        return self.ai_schedule_manager._handle_general_respond(prompt, user_input)  # 直接返回通用回复