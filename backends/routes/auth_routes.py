from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from flask import session
from typing import List, Dict

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
def load_logged_in_user():
    """Load the logged-in user from the session."""
    user_id = session.get('user_id', None)
    if user_id is None:
        try:
            user_id = request.args.get('user_id', None)
        except:
            user_id = None
    # print(f"User ID from session: {user_id}")
    
    if user_id is not None:
        from core.core import scheduler
        scheduler.login(user_id)
        g.user = user_id
    else:
        g.user = None
        # return jsonify({'success': False, 'error': 'No user is currently logged in.'}), 401

@bp.route('/register',  methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        # username = request.form['username']
        # password = request.form['password']
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                from core.core import auth_manager
                auth_manager.add_user(username, password)
            except Exception as e:
                error = str(e)
            else:
                return jsonify({'success': True})
            
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
    return jsonify({'success': False, 'error': 'Invalid request method.'}), 405


@bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # username = request.form['username']
        # password = request.form['password']
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                from core.core import auth_manager
                user = auth_manager.authenticate(username, password)
                if user:
                    session['user_id'] = user['id']

                    # Log the user
                    # from core.core import scheduler
                    # scheduler.login(user['id'])

                    return jsonify({'success': True, 'user_id': user['id']})
                else:
                    error = 'Failed to authenticate user.'
            except Exception as e:
                error = str(e)

        return jsonify({'success': False, 'error': error})
    return jsonify({'success': False, 'error': 'Invalid request method.'}), 405

@bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    
    if user_id:
        # Log the user out
        from core.core import scheduler
        scheduler.logout()
    else:
        return jsonify({'success': False, 'error': 'No user is currently logged in.'})
    
    session.pop('user_id', None)

    return jsonify({'success': True})

def login_required(view):
    """Decorator to ensure the user is logged in."""
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({'success': False, 'error': 'User not logged in.'}), 401
        return view(**kwargs)
    return wrapped_view
