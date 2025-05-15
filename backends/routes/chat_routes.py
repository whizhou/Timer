from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from flask import session

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
        # data = request.get_json()
        # message = data.get('message')
        message = request.form.get('message')  # Not using JSON for simplicity
        if not message:
            return jsonify({'error': 'No message provided'}), 400
    else:
        return jsonify({'error': 'Invalid request method'}), 405

    
    # Here you would typically process the message and get a response
    # For now, we'll just echo the message back
    response = f"You said: {message}"
    messages = session.get('messages', [])


    messages.append({'role': 'user', 'content': message})
    messages.append({'role': 'assistant', 'content': response})

    session['messages'] = messages

    return jsonify({'messages': messages}), 200
