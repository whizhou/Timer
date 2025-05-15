from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from flask import session
from typing import List, Dict

bp = Blueprint('schedule', __name__, url_prefix='/schedule')


@bp.route('/', methods=['GET', 'POST'])
def schedule():
    """
    Handle schedule requests.
    - GET: Return all schedules in a JSON file
    - POST: Receive user input for task content, generate schedule and return JSON data
    """
    from core.scheduler import scheduler
    if request.method == 'POST':
        data = request.get_json()
        schedule_content = data.get('schedule')
        # Generate schedule based on user input
        schedule_id = scheduler.create_schedule(schedule_content)
        return jsonify({'id': schedule_id})
    else:
        # Return all schedules in a JSON file
        schedules: Dict = scheduler.get_schedules()
        return jsonify(schedules)
    
@bp.route('/<int:schedule_id>', methods=['GET', 'PUT', 'DELETE'])
def schedule_by_id(schedule_id: int):
    """
    Handle schedule requests by ID.
    - GET: Return schedule by ID
    - PUT: Update schedule by ID
    - DELETE: Delete schedule by ID
    """
    from core.scheduler import scheduler
    if request.method == 'GET':
        # Get schedule by ID
        schedule: Dict | None = scheduler.get_schedule_by_id(schedule_id)
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        schedule = {'schedule': schedule}  # Wrap in a dictionary
        return jsonify(schedule)
    elif request.method == 'PUT':
        # Update schedule by ID
        data = request.get_json()
        updated_schedule = data.get('schedule')
        success = scheduler.update_schedule(updated_schedule)
        return jsonify({'success': success})
    elif request.method == 'DELETE':
        # Delete schedule by ID
        success = scheduler.delete_schedule(schedule_id)
        return jsonify({'success': success})
    else:
        return jsonify({'error': 'Invalid request method'}), 405
    
@bp.route('/archive/<int:schedule_id>', methods=['POST'])
def archive_schedule(schedule_id: int):
    """
    Archive a schedule by ID.
    """
    from core.scheduler import scheduler
    success = scheduler.archive_schedule(schedule_id)
    return jsonify({'success': success})

@bp.route('/remind', methods=['GET'])
def remind():
    """
    Get the list of schedule IDs for reminders.
    """
    from core.scheduler import scheduler
    schedule_id_list: List[int] = scheduler.get_reminders()
    return jsonify({'schedule_id_list': schedule_id_list})

@bp.route('sync', methods=['GET'])
def sync():
    """
    Sync schedules with the backend.
    """
    from core.scheduler import scheduler
    data = request.get_json()
    info = data.get('info')
    assert type(info) == list, "info should be a list"
    # Synchronize schedules with the backend
    schedules_to_sync: List[Dict] = scheduler.sync_schedules(info)
    return jsonify({'schedules': schedules_to_sync})
