import pytest
import json
import random
import datetime
from flask import jsonify
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch


ROOT_DIR = Path(__file__).resolve().parent.parent
example_schedules_path = ROOT_DIR / 'data' / 'example_schedules.json'
example_schedules = json.loads(example_schedules_path.read_text(encoding='utf-8'))
example_schedules = example_schedules['schedules']

# print(example_schedules)

@pytest.fixture
def client(app):
    """Fixture for Flask test client"""
    return app.test_client()

def get_test_schedules():
    """Helper function to load testing schedules from JSON file."""
    test_schedules_path = ROOT_DIR / 'data/schedules' / '1.json'
    test_schedules = json.loads(test_schedules_path.read_text(encoding='utf-8'))
    return test_schedules['schedules']

def test_schedule_get_all(client):
    """Test GET /schedule/ returns all schedules"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': '123'
    })
    assert response.status_code == 200

    response = client.get('/schedule/')
    response_data = response.get_json()
    test_schedules = get_test_schedules()

    assert response.status_code == 200
    assert 'schedules' in response_data
    assert isinstance(response_data['schedules'], list)
    assert response_data['schedules'] == test_schedules, \
           "Returned schedules do not match test schedules"

def test_schedule_post_create(client):
    """Test POST /schedule/ creates a new schedule"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': '123'
    })
    assert response.status_code == 200
    for new_schedule in example_schedules:
        new_schedule = example_schedules[0]
        new_schedule['id'] = random.randint(10000, 99999)
        response = client.post('/schedule/', json={'schedules': [new_schedule]})
        created_schedule_id = response.get_json()['ids'][0]

        test_schedules = get_test_schedules()
        new_created_schedule = test_schedules[-1]  # Assuming the new schedule is added at the end

        assert response.status_code == 200
        assert created_schedule_id == new_created_schedule['id'], \
            "Created schedule ID does not match the expected ID"


def test_schedule_get_by_id_found(client):
    """Test GET /schedule/<id> returns schedule when found"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': '123'
    })
    assert response.status_code == 200
    for schedule in get_test_schedules():
        # print(type(schedule))
        response = client.get(f'/schedule/{schedule["id"]}')
        assert response.status_code == 200
        assert response.json == {'schedule': schedule}


def test_schedule_get_by_id_not_found(client):
    """Test GET /schedule/<id> returns 404 when not found"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': '123'
    })
    assert response.status_code == 200
    response = client.get('/schedule/999')
    assert response.status_code == 404
    assert response.json == {'error': 'Schedule not found'}


def test_schedule_update(client):
    """Test PUT /schedule/<id> updates schedule"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': '123'
    })
    assert response.status_code == 200
    test_schedules = get_test_schedules()
    for schedule in test_schedules:
        response = client.put(f'/schedule/{schedule["id"]}', json={'schedule': schedule})
        assert response.status_code == 200
        assert response.json == {'success': True}

    response = client.put('/schedule/999', json={'schedule': {'content': 'Updated content', 'id': 999}})
    assert response.status_code == 200
    assert response.json == {'success': False}


def test_schedule_delete(client):
    """Test DELETE /schedule/<id> deletes schedule"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': '123'
    })
    assert response.status_code == 200
    test_schedules = get_test_schedules()
    for schedule in random.sample(test_schedules, 1):  # Delete 1 random schedules
        response = client.delete(f'/schedule/{schedule["id"]}')
        assert response.status_code == 200
        assert response.json == {'success': True}

    response = client.delete('/schedule/999')
    assert response.status_code == 200
    assert response.json == {'success': False}


def test_archive_schedule(client):
    """Test GET /schedule/archive/<id> archives schedule"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': '123'
    })
    assert response.status_code == 200
    test_schedules = get_test_schedules()
    for schedule in random.sample(test_schedules, 1):
        response = client.get(f'/schedule/archive/{schedule["id"]}')
        assert response.status_code == 200
        assert response.json == {'success': True}

    response = client.get('/schedule/archive/999')
    assert response.status_code == 200
    assert response.json == {'success': False}



def test_get_remind_start(client):
    """Test GET /schedule/remind_start returns reminder IDs"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': '123'
    })
    assert response.status_code == 200
    test_schedules = get_test_schedules()
    test_schedules = [s for s in test_schedules if 'remind_start' in s]
    response = client.get('/schedule/remind_start')
    assert response.status_code == 200
    assert response.json == {'schedules': test_schedules}


def test_get_remind_before(client):
    """Test GET /schedule/remind_before returns reminder IDs"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': '123'
    })
    assert response.status_code == 200
    test_schedules = get_test_schedules()
    test_schedules = [s for s in test_schedules if 'remind_before' in s]
    response = client.get('/schedule/remind_before')
    print(response.json)
    assert response.status_code == 200
    assert response.json == {'schedules': test_schedules}

def test_get_running(client):
    """Test GET /schedule/running returns running schedule IDs"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': '123'
    })
    assert response.status_code == 200
    test_schedules = get_test_schedules()
    # test_schedules = [s for s in test_schedules if 'remind_before' in s]
    response = client.get('/schedule/running')
    print(response.json)
    assert response.status_code == 200
    # assert response.json == {'schedules': test_schedules}

def test_sync_schedules(client):
    """Test GET /schedule/sync syncs schedules"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': '123'
    })
    assert response.status_code == 200
    test_schedules = get_test_schedules()
    for idx, schedule in enumerate(test_schedules):
        # Modify the schedule to simulate a sync
        test_schedules[idx]['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response = client.get('/schedule/sync', json={'schedules': test_schedules})
    test_schedules = get_test_schedules()
    assert response.status_code == 200    
    assert response.json == {'schedules': test_schedules}
    
def test_pet_routes(client):
    """Test GET /tomorrow/<id>/titles and /quantity routes"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': '123'
    })
    assert response.status_code == 200
    for i in range(3):
        response_titles = client.get(f"/schedule/titles/{i}")
        assert response_titles.status_code == 200
        assert isinstance(response_titles.json, dict)

        response_quantity = client.get(f"/schedule/quantity/{i}")
        assert response_quantity.status_code == 200
        assert isinstance(response_quantity.json, dict)

'''
def test_invalid_method(client):
    """Test invalid methods return 405"""
    response = client.patch('/schedule/1')
    assert response.status_code == 405
    assert response.json == None
'''