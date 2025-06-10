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
            - session_id (str, optional): Explicit session ID for tracking conversations.
                If provided, this will override the cookie-based session.
            - cookie (str): The cookie value for session management.
                session (str): The session ID for tracking user sessions.
    """
    if request.method == 'POST':
        # Get the message from the request
        data = request.get_json()
        message = data.get('message')  # Get message from JSON payload
        # 获取可选的session_id参数
        custom_session_id = data.get('session_id')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
    else:
        return jsonify({'error': 'Invalid request method'}), 405
    
    # 如果提供了自定义session_id，使用它来获取或创建会话
    if custom_session_id:
        # 更简单的方法：直接使用Flask的会话机制，但手动设置会话ID
        from flask import current_app
        import os
        from flask.sessions import SecureCookieSession
        
        # 获取会话文件路径
        session_path = os.path.join(current_app.config.get('SESSION_FILE_DIR', 'flask_session'), 
                                   f'session-{custom_session_id}')
        
        # 尝试读取会话文件
        if os.path.exists(session_path):
            try:
                import pickle
                with open(session_path, 'rb') as f:
                    session_data = pickle.load(f)
                    messages = session_data.get('messages', None)
            except Exception as e:
                print(f"Error loading session: {e}")
                messages = None
        else:
            # 如果会话不存在，创建一个新的
            messages = None
            
        # 如果没有找到会话或出错，设置为None
        if messages is None:
            messages = [{'role': 'system', 'content': "你是Timer，一个智能的日程助手，擅长从学生输入的任务中提取关键信息（如截止时间、任务内容），并智能推断合理的日程标题、主要内容、预计耗时、最晚开始时间。"}]
    else:
        # 使用标准的Flask会话
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

    # 保存会话数据
    if custom_session_id:
        # 如果使用自定义session_id，直接写入文件系统
        try:
            import pickle
            import os
            
            # 确保会话目录存在
            session_dir = current_app.config.get('SESSION_FILE_DIR', 'flask_session')
            os.makedirs(session_dir, exist_ok=True)
            
            # 保存会话数据
            session_path = os.path.join(session_dir, f'session-{custom_session_id}')
            session_data = {'messages': messages}
            with open(session_path, 'wb') as f:
                pickle.dump(session_data, f)
            
            print(f"Session saved to {session_path}")
        except Exception as e:
            print(f"Error saving session: {e}")
        
        # 返回结果时包含session_id
        return jsonify({
            'messages': messages, 
            'response': response,
            'session_id': custom_session_id
        }), 200
    else:
        # 使用标准Flask会话
        session['messages'] = messages
        
        # 从当前响应中获取session_id
        current_session_id = session.sid if hasattr(session, 'sid') else None
        
        return jsonify({
            'messages': messages, 
            'response': response,
            'session_id': current_session_id
        }), 200
