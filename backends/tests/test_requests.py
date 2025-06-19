import pytest
import json
import random
import requests
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
example_schedules_path = ROOT_DIR / 'data' / 'example_schedules.json'
example_schedules = json.loads(example_schedules_path.read_text(encoding='utf-8'))
example_schedules = example_schedules['schedules']

BASE_URL = "http://127.0.0.1:5000"

def get_test_schedules():
    """Helper function to load testing schedules from JSON file."""
    test_schedules_path = ROOT_DIR / 'data' / 'dev.json'
    test_schedules = json.loads(test_schedules_path.read_text(encoding='utf-8'))
    return test_schedules['schedules']

def test_schedule_get_all():
    """Test GET /schedule/ returns all schedules"""
    test_schedules = get_test_schedules()

    response = requests.get(f"{BASE_URL}/schedule/")
    response_data = response.json()

    assert response.status_code == 200
    assert 'schedules' in response_data
    assert isinstance(response_data['schedules'], list)
    assert response_data['schedules'] == test_schedules, \
           "Returned schedules do not match test schedules"

def test_schedule_post_create():
    """Test POST /schedule/ creates a new schedule"""
    for new_schedule in example_schedules:
        new_schedule = example_schedules[0]
        new_schedule['id'] = random.randint(10000, 99999)
        response = requests.post(
            f"{BASE_URL}/schedule/", 
            json={'schedules': [new_schedule]},
            headers={'Content-Type': 'application/json'}
        )
        created_schedule_id = response.json()['ids'][0]

        test_schedules = get_test_schedules()
        new_created_schedule = test_schedules[-1]  # Assuming the new schedule is added at the end

        assert response.status_code == 200
        assert created_schedule_id == new_created_schedule['id'], \
            "Created schedule ID does not match the expected ID"

def test_schedule_get_by_id_found():
    """Test GET /schedule/<id> returns schedule when found"""
    for schedule in get_test_schedules():
        response = requests.get(f"{BASE_URL}/schedule/{schedule['id']}")
        assert response.status_code == 200
        assert response.json() == {'schedule': schedule}

def test_schedule_get_by_id_not_found():
    """Test GET /schedule/<id> returns 404 when not found"""
    response = requests.get(f"{BASE_URL}/schedule/999")
    assert response.status_code == 404
    assert response.json() == {'error': 'Schedule not found'}

def test_schedule_update():
    """Test PUT /schedule/<id> updates schedule"""
    test_schedules = get_test_schedules()
    for schedule in test_schedules:
        response = requests.put(
            f"{BASE_URL}/schedule/{schedule['id']}", 
            json={'schedule': schedule},
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 200
        assert response.json() == {'success': True}

    response = requests.put(
        f"{BASE_URL}/schedule/999", 
        json={'schedule': {'content': 'Updated content', 'id': 999}},
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 200
    assert response.json() == {'success': False}

def test_schedule_delete():
    """Test DELETE /schedule/<id> deletes schedule"""
    test_schedules = get_test_schedules()
    for schedule in random.sample(test_schedules, 1):  # Delete 1 random schedules
        response = requests.delete(f"{BASE_URL}/schedule/{schedule['id']}")
        assert response.status_code == 200
        assert response.json() == {'success': True}

    response = requests.delete(f"{BASE_URL}/schedule/999")
    assert response.status_code == 200
    assert response.json() == {'success': False}

def test_archive_schedule():
    """Test GET /schedule/archive/<id> archives schedule"""
    test_schedules = get_test_schedules()
    for schedule in random.sample(test_schedules, 1):
        response = requests.get(f"{BASE_URL}/schedule/archive/{schedule['id']}")
        assert response.status_code == 200
        assert response.json() == {'success': True}

    response = requests.get(f"{BASE_URL}/schedule/archive/999")
    assert response.status_code == 200
    assert response.json() == {'success': False}

def test_get_remind_start():
    """Test GET /schedule/remind_start returns reminder IDs"""
    test_schedules = get_test_schedules()
    test_schedules = [s for s in test_schedules if 'remind_start' in s]
    response = requests.get(f"{BASE_URL}/schedule/remind_start")
    assert response.status_code == 200
    assert response.json() == {'schedules': test_schedules}

def test_get_remind_before():
    """Test GET /schedule/remind_before returns reminder IDs"""
    test_schedules = get_test_schedules()
    test_schedules = [s for s in test_schedules if 'remind_before' in s]
    response = requests.get(f"{BASE_URL}/schedule/remind_before")
    assert response.status_code == 200
    assert response.json() == {'schedules': test_schedules}

def test_sync_schedules():
    """Test GET /schedule/sync syncs schedules"""
    test_schedules = get_test_schedules()
    for idx, schedule in enumerate(test_schedules):
        # Modify the schedule to simulate a sync
        test_schedules[idx]['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response = requests.get(
        f"{BASE_URL}/schedule/sync", 
        json={'schedules': test_schedules},
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 200    
    assert response.json() == {'schedules': test_schedules}
