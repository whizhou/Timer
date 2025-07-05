from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from flask import session
from flask import current_app
from openai import OpenAI
from typing import Dict, Union, List
from datetime import datetime, timedelta

bp = Blueprint('chat', __name__, url_prefix='/chat')

# @bp.before_request
# def before_request():
#     session.permanent = True  # 设置session为持久化
#     session.modified = True

@bp.before_request
def check_logged_in():
    """
    Check if the user is logged in before processing the request.
    If not logged in, return an error response.
    """
    if g.user is None:
        return jsonify({'success': False, 'error': 'User not logged in.'}), 401

@bp.route('/', methods=['POST'])
def chat():
    """
    Handle chat requests.
    All messages data is stored in the session which is stored in the filesystem.
    - POST: Receive user input for chat content, generate response and return JSON data

        Args:
            - message (str): The user input message.
            - cookie (str): The cookie value for session management.
                session (str): The session ID for tracking user sessions.
    """
    if request.method == 'POST':
        # Get the message from the request
        data = request.get_json()
        message = data.get('message')  # Get message from JSON payload
        # message = request.form.get('message')  # Not using JSON for simplicity
        if not message:
            return jsonify({'error': 'No message provided'}), 400
    else:
        return jsonify({'error': 'Invalid request method'}), 405

    # messages: List[Dict] = session.get('messages', [])

    from core.core import scheduler
    # print(f"Received message: {message}")
    res = scheduler.process_user_request({'word': message})
    schedule: Dict = {}
    response: str = ""
    if isinstance(res, dict):
        if res['status'] == 'error':
            # success = False
            response = res['error']  # 先把错误信息返回前端输出

        elif res['action'] == 'create':
            schedule = res['schedule_data']
            response = f"成功创建日程: {schedule['content']['title']} (id={schedule['id']})"

        elif res['action'] == 'modify':
            schedule = res['modified']
            assert schedule['id'] == res['schedule_id'], "Schedule ID mismatch"
            response = f"成功更新日程: {schedule['content']['title']} (id={res['schedule_id']})"

        elif res['action'] == 'delete':
            response = f"成功删除日程: {res['schedule_title']} (id={res['schedule_id']})"

        elif res['action'] == 'inquery':
            schedule_list = res['schedule_list']

            ds_messages = [
                {'role': 'system', 'content': '你是一个日程播报助手，负责播报用户的日程信息。要求：\n1. 以 Markdown 格式输出。\n2. 只播报日程内容，不需要其他信息。\n3.信息播报时，保持语言简洁，适当使用表情符号。'
                    '\n4. 只播报日程，不要多余。'},
                {'role': 'user', 'content': f"需要播报的日程列表: {schedule_list}"}
            ]

            client = OpenAI(api_key=current_app.config['DEEPSEEK_API_KEY'], base_url="https://api.deepseek.com")
            ds_response = client.chat.completions.create(
                model="deepseek-chat",
                messages=ds_messages,  # type: ignore
                stream=False,
            )

            response = ds_response.choices[0].message.content.strip()  # type: ignore

        else:
            raise ValueError(f"Unexpected action type: {res['action']}")
    elif isinstance(res, str):
        response = res
    else:
        raise ValueError("Unexpected response type from process_user_request")

    # messages.append({'role': 'user', 'content': message})
    assistant_message = {
        'role': 'assistant',
        'content': response,
        'schedule': schedule
    }
    # messages.append(assistant_message)

    # session['messages'] = messages

    return jsonify({'messages': [], 'response': response, 'schedule': schedule}), 200


@bp.route('/pet_chat', methods=['POST'])
def pet_chat():
    """
    Handle chat requests.
    All messages data is stored in the session which is stored in the filesystem.
    - POST: Receive user input for chat content, generate response and return JSON data

        Args:
            - message (str): The user input message.
            - cookie (str): The cookie value for session management.
                session (str): The session ID for tracking user sessions.
    """
    if request.method == 'POST':
        # Get the message from the request
        data = request.get_json()
        message = data.get('message')  # Get message from JSON payload
        if not message:
            return jsonify({'error': 'No message provided'}), 400
    else:
        return jsonify({'error': 'Invalid request method'}), 405

    # messages: List[Dict] = session.get('messages', [])

    from core.core import scheduler
    # print(f"Received message: {message}")
    res = scheduler.process_user_request({'word': message})
    schedule: Dict = {}
    response: str = ""
    if isinstance(res, dict):
        if res['status'] == 'error':
            # success = False
            response = res['error']  # 先把错误信息返回前端输出

        elif res['action'] == 'create':
            schedule = res['schedule_data']
            response = f"成功创建日程"

        elif res['action'] == 'modify':
            schedule = res['modified']
            assert schedule['id'] == res['schedule_id'], "Schedule ID mismatch"
            response = f"成功更新日程"

        elif res['action'] == 'delete':
            response = f"成功删除日程"

        elif res['action'] == 'inquery':
            schedule = res['schedule_list']
            response = "成功查询日程"
        else:
            raise ValueError(f"Unexpected action type: {res['action']}")
        
        if res['status'] != 'error':
            schedule_list = [schd['content'] for schd in schedule] if isinstance(schedule, list) else [schedule['content']]
            ds_messages = [
                {'role': 'system', 'content': '你是一个日程助手桌面宠物，请根据用户信息和日程内容进行播报。要求：\n1. 只输出文字，不要有特殊符号。\n'
                    '2. 模仿桌面宠物的语气回复，语气日常一点、不要太过热情，可以的话偶尔在每句话最后加个\"喵\"'},
                {'role': 'user', 'content': f"{response}, 需要播报的日程列表: {schedule_list}"}
            ]
            client = OpenAI(api_key=current_app.config['DEEPSEEK_API_KEY'], base_url="https://api.deepseek.com")
            ds_response = client.chat.completions.create(
                model="deepseek-chat",
                messages=ds_messages,  # type: ignore
                stream=False,
            )
            response = ds_response.choices[0].message.content.strip()  # type: ignore

    elif isinstance(res, str):
        response = res
    else:
        raise ValueError("Unexpected response type from process_user_request")

    # messages.append({'role': 'user', 'content': message})
    # assistant_message = {
    #     'role': 'assistant',
    #     'content': response,
    #     'schedule': schedule
    # }
    # messages.append(assistant_message)

    # session['messages'] = messages

    return jsonify({'response': response}), 200

@bp.route('/remind', methods=['GET'])
def remind():
    """
    Handle reminder requests.
    - GET: Return a reminder message for the user.

        Args:
            - cookie (str): The cookie value for session management.
            - session (str): The session ID for tracking user sessions.
    """
    from core.core import scheduler
    schedules = scheduler.get_running_schedules()
    today_schedules = []
    target_date = (datetime.now() + timedelta(days=0)).date()
    for schedule in schedules:
        schedule_date = datetime.strptime(schedule['content']['end_time'][0], '%Y-%m-%d').date()
        if schedule_date == target_date:
            today_schedules.append(schedule['content'])

    response = '📅今天的日程安排如下：\n\n'
    for content in today_schedules:
        response += f"📅{content['title']}\n"

        if 'begin_time' in content and 'end_time' in content:
            start_time = ' '.join(content['begin_time'])
            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').strftime('%m月%d日 %H:%M')
            end_time = ' '.join(content['end_time'])
            end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').strftime('%m月%d日 %H:%M')
            response += f" - ⏰ {start_time} - {end_time}\n"
        elif 'end_time' in content:
            end_time = ' '.join(content['end_time'])
            end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').strftime('%m月%d日 %H:%M')
            response += f" - ⏰ {end_time}\n"

        if 'location' in content:
            response += f" - 📍 {content['location']}\n"

        if content.get('tag', 'default') != 'default':
            response += f" - 🏷️  {content['tag']}"
        
        response += '\n\n'

    # ds_messages = [
    #     {'role': 'system', 'content': '你是一个日程播报助手，负责播报用户今日的日程信息。要求：\n1. 以 Markdown 格式输出。\n2. 只播报日程内容，不需要其他信息。\n3.信息播报时，保持语言简洁，适当使用表情符号。'
    #         '\n4. 只播报日程，不要多余。'},
    #     {'role': 'user', 'content': f"需要播报的日程列表: {today_schedules}"}
    # ]

    # client = OpenAI(api_key=current_app.config['DEEPSEEK_API_KEY'], base_url="https://api.deepseek.com")
    # ds_response = client.chat.completions.create(
    #     model="deepseek-chat",
    #     messages=ds_messages,  # type: ignore
    #     stream=False,
    # )

    # response = ds_response.choices[0].message.content.strip()  # type: ignore

    # print(response)

    return jsonify({'response': response}), 200