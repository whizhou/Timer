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

    Returns:
    - POST: {'id': schedule_ids}, where schedule_ids is the list of IDs of the created schedules
    - GET: JSON data containing the schedule information in the following format:

        {
        "schedules": [
            {
                "id": "the id of the schedule",
            "timestamp": "last modified time, in YYYY-MM-DD HH:MM:SS format",
            "type": "schedule",
            "content": {
                "title": "the title of the schedule",
                "content": "the content of the schedule (optional)",
                "whole_day": "bool: whether the schedule is a whole day event",
                "begin_time": ["YYYY-MM-DD", "HH:MM (default 08:00)"],
                "end_time": ["YYYY-MM-DD", "HH:MM (default 23:59)"],
                "location": "the location of the schedule (optional)",
                "remind_before": "the time (in minutes) to remind before the schedule starts (optional)",
                "tag": "the tag of the schedule (optional)",
                "repeat": {
                    "repeat": "bool: whether the schedule is a repeat event",
                    "type": "the type of repeat (e.g., daily, weekly, monthly) (optional)",
                    "every": "the interval of repeat (e.g., 1) (optional)",
                    "repeat_until": ["YYYY-MM-DD", "HH:MM (default 23:59)"]
                },
                "additional_info": [
                    "any additional information related to the schedule (optional)",
                    "this can include links, notes, or any other relevant details",
                    "without any specific format, just plain text"
                ]
            },
            {
                ...
            }
        ]
        }
    """
    from core.core import scheduler
    if request.method == 'POST':
        data = request.get_json()
        schedules: List[Dict] = data.get('schedules', [])
        # Generate schedule based on user input
        schedule_ids: List[int] = scheduler.create_schedule(schedules)
        return jsonify({'ids': schedule_ids})
    else:
        # Return all schedules in a JSON file
        schedules: List[Dict] = scheduler.get_schedules()
        return jsonify({'schedules': schedules})
    
@bp.route('/<int:schedule_id>', methods=['GET', 'PUT', 'DELETE'])
def schedule_by_id(schedule_id: int):
    """
    Handle schedule requests by ID.
    - GET: Return schedule by ID
    - PUT: Update schedule by ID
    - DELETE: Delete schedule by ID

    Returns:
    - GET - JSON: {'schedule': schedule}, where schedule is the schedule with the given ID
    - PUT - JSON: {'success': True} if update was successful, otherwise {'success': False}
    - DELETE - JSON: {'success': True} if delete was successful, otherwise {'success': False}
    """
    from core.core import scheduler
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
        updated_schedule = data.get('schedule', None)

        if not updated_schedule:
            return jsonify({'error': 'No schedule data provided'}), 400
        elif not isinstance(updated_schedule, dict):
            return jsonify({'error': 'Invalid schedule data format'}), 400
        
        success = scheduler.update_schedule(updated_schedule)
        return jsonify({'success': success}) 
    elif request.method == 'DELETE':
        # Delete schedule by ID
        success = scheduler.delete_schedule(schedule_id)
        return jsonify({'success': success})
    else:
        return jsonify({'error': 'Invalid request method'}), 405
    
@bp.route('/archive/<int:schedule_id>', methods=['GET'])
def archive_schedule(schedule_id: int):
    """
    Archive a schedule by ID.
    Returns:
        JSON: {'success': True/False}
    """
    from core.core import scheduler
    success = scheduler.archive_schedule(schedule_id)
    return jsonify({'success': success})

@bp.route('/remind_start', methods=['GET'])
def remind_start():
    """
    Get the schedules for reminders.

    Returns:
        JSON: {'schedules': schedules whose reminder is started}
    """
    from core.core import scheduler
    schedules = scheduler.get_remind_start()
    return jsonify({'schedules': schedules})

@bp.route('/remind_before', methods=['GET'])
def remind():
    """
    Get the schedules that are becoming active or are active.
    Returns:
        JSON: {'schedules': schedules running or going to run}
    """
    from core.core import scheduler
    schedules = scheduler.get_remind_before()
    return jsonify({'schedules': schedules})

@bp.route('/sync', methods=['GET'])
def sync():
    """
    Sync schedules with the backend.

    Receive:
        List[Dict]: schedules - List of schedules to be synchronized

    Returns:
        List[Dict]: The synchronized schedules
    """
    from core.core import scheduler
    data = request.get_json()
    schedules: List[Dict] = data.get('schedules', [])
    # Synchronize schedules with the backend
    schedules_synced: List[Dict] = scheduler.sync_schedules(schedules)
    return jsonify({'schedules': schedules_synced})

@bp.route('/quantity', methods=['GET'])
def quantity():
    """
    Get the quantity of schedules.

    Returns:
        JSON: {'quantity': int} - The number of waiting or running schedules
    """
    from core.core import scheduler
    quantity = scheduler.get_schedule_quantity()
    return jsonify({'quantity': quantity})

@bp.teardown_request
def teardown_request(exception):
    """
    Teardown request to clean up resources.
    """
    # Here you can add any cleanup code if needed
    from core.core import scheduler
    scheduler.save()