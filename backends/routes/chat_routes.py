from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from flask import session
from flask import current_app
from openai import OpenAI
from typing import Dict, Union, List

bp = Blueprint('chat', __name__, url_prefix='/chat')

# @bp.before_request
# def before_request():
#     session.permanent = True  # 设置session为持久化
#     session.modified = True

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

    messages: List[Dict] = session.get('messages', [])

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
    messages.append(assistant_message)

    session['messages'] = messages

    return jsonify({'messages': messages, 'response': response, 'schedule': schedule}), 200
