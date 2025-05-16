from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from flask import session
from flask import current_app
from openai import OpenAI

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

    messages = session.get('messages', None)
    ##########################################################################
    # Here you would typically process the message and get a response
    # For now, we'll just echo the message back

    if messages is None:
        messages = [{'role': 'system', 'content': "你是Timer，一个智能的日程助手，擅长从学生输入的任务中提取关键信息（如截止时间、任务内容），并智能推断合理的日程标题、主要内容、预计耗时、最晚开始时间。"}]
    messages.append({'role': 'user', 'content': message})
    client = OpenAI(api_key=current_app.config['DEEPSEEK_API_KEY'], base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,  # type: ignore
        stream=False,
    )
    response = response.choices[0].message.content
    ##########################################################################

    # messages.append({'role': 'user', 'content': message})
    messages.append({'role': 'assistant', 'content': response})

    session['messages'] = messages

    return jsonify({'messages': messages, 'response': response}), 200
