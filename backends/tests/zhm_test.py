import json
import sys
import os
import copy
from datetime import datetime, timedelta

# 获取当前文件的目录（tests/）
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（tests/ 的父目录）
project_root = os.path.dirname(current_dir)
# 添加到 Python 路径
sys.path.append(project_root)

# 导入必要的模块
from flask import Flask
from flask_session import Session
from config.config import DevelopmentConfig
from core.core import scheduler
# from core.ai_scheduler import AIScheduler
from core.ai_scheduler2 import AIScheduler
from core.scheduler import Scheduler  # 新增导入

# 测试数据
existing_schedules = [
    {
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


def demonstrate_usage():
    """展示函数使用方法的示例（独立演示）"""
    # 创建测试应用
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    app.config['TESTING'] = True
    Session(app)
    scheduler.init_app(app)
    
    # 初始化 AIScheduler
    ai_scheduler = AIScheduler(app)
    
    # 注入测试数据，避免空日程导致 ValueError
    ai_scheduler.create_schedule(copy.deepcopy(existing_schedules)) 
    
    # 测试用例
    test_cases = [
        "明天下午3点有个会议",  # 隐含创建意图
        "修改概率论作业时间为明天下午3点开始，明晚截止",
        "把会议时间改到4点",  # 隐含修改意图
        "删除线性代数实验任务",
        "取消明天的会议",     # 隐含删除意图
        "今天天气怎么样",     # 通用意图
        "帮我记一下，下一个周五要交作业"  # 隐含创建意图
    ]
    
    for case in test_cases:
        print(f"\n输入: {case}")
        print("-" * 50)
        
        result = ai_scheduler.process_user_request(case)
        
        # 根据返回类型进行不同格式的输出
        if isinstance(result, dict):
            print("[特定意图处理结果]")
            print(f"操作类型: {result.get('action', '未知')}")
            print(f"状态: {result.get('status', '未知')}")
            
            if result.get('action') == 'create':
                print(f"日程类型: {result.get('type', '未知')}")
                print("日程详情:")
                print(json.dumps(result.get('schedule_data', {}), indent=2, ensure_ascii=False))
                
            elif result.get('action') == 'modify':
                print(f"日程ID: {result.get('schedule_id', '未知')}")
                print("原始内容:")
                print(json.dumps(result.get('original', {}), indent=2, ensure_ascii=False))
                print("修改后内容:")
                print(json.dumps(result.get('modified', {}), indent=2, ensure_ascii=False))
                
            elif result.get('action') == 'delete':
                print(f"删除的日程ID: {result.get('schedule_id', '未知')}")
                print(f"日程标题: {result.get('schedule_title', '未知')}")
                
        else:
            print("[通用对话响应]")
            print(result)
        
        # # 输出当前日程库（直接用 ai_scheduler 的 scheduler）
        # schedules = ai_scheduler.scheduler.get_schedules()
        # print("\n[当前日程库内容]:")
        # print(json.dumps(schedules, indent=2, ensure_ascii=False))
        # print("-" * 50)

if __name__ == "__main__":
    print("\n\n=== 功能演示 ===")
    demonstrate_usage()
