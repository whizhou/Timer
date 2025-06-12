import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from unittest.mock import patch, MagicMock
from backends.core.ai_scheduler2 import AIScheduler
from textwrap import dedent

@patch('backends.core.ai_scheduler.parse_schedule')
@patch.object(AIScheduler, 'create_schedule')
def test_create_json(mock_create_schedule, mock_parse_schedule, scheduler):
    # Arrange
    mock_ai_result = {'mock': 'json'}
    mock_parse_schedule.return_value = mock_ai_result
    mock_create_schedule.return_value = [1]  # 假设返回的 schedule_id 是 1

    input_text = "创建数值分析作业\n"
    input_text += dedent("""
    @所有人 同学们，本周作业是：教材第136页的"习题"中的题 10；18；以及教材第175-176页的"习题"中的 题 1；7 。下周三交作业。
    """).strip()

    existing_schedules = []

    # Act
    result = scheduler.create_json(input_text, existing_schedules)
    print("\nResult:", result)  # 应该输出 [1]

    # Assert
    mock_parse_schedule.assert_called_once_with(input_text, existing_schedules=existing_schedules)
    mock_create_schedule.assert_called_once_with([mock_ai_result])
    assert result == [1]

    # 模拟 get_schedule_by_id 并打印调试信息
    with patch.object(AIScheduler, 'get_schedule_by_id', return_value={"id": 1, "title": "数值分析作业"}):
        print("\nDebugging schedule output:")
        for schedule_id in result:
            schedule_dict = scheduler.get_schedule_by_id(schedule_id)
            print(f"Schedule ID: {schedule_id}")
            if schedule_dict:
                for k, v in schedule_dict.items():
                    print(f"{k}: {v}")
            else:
                print("No schedule found.")