import pytest
import json
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

def test_schedule_get_all(client):
    """Test GET /schedule/ returns all schedules"""
    response = client.get('/schedule/')
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert 'schedules' in response_data
    assert isinstance(response_data['schedules'], list)
    assert len(response_data['schedules']) == 3

def test_schedule_post_create(client):
    """Test POST /schedule/ creates a new schedule"""
    response = client.post('/schedule/', json={'schedule': {'content': 'Test content'}})
    assert response.status_code == 200
    assert response.json == {'id': -1}

def test_schedule_get_by_id_found(client):
    """Test GET /schedule/<id> returns schedule when found"""
    for schedule in example_schedules:
        # print(type(schedule))
        response = client.get(f'/schedule/{schedule["id"]}')
        assert response.status_code == 200
        assert response.json == {'schedule': schedule}


def test_schedule_get_by_id_not_found(client):
    """Test GET /schedule/<id> returns 404 when not found"""
    response = client.get('/schedule/999')
    assert response.status_code == 404
    assert response.json == {'error': 'Schedule not found'}

def test_schedule_update(client):
    """Test PUT /schedule/<id> updates schedule"""
    for schedule in example_schedules:
        response = client.put(f'/schedule/{schedule["id"]}', json={'schedule': schedule})
        assert response.status_code == 200
        assert response.json == {'success': True}
    response = client.put('/schedule/999', json={'schedule': {'content': 'Updated content'}})
    assert response.status_code == 200
    assert response.json == {'success': False}

def test_schedule_delete(client):
    """Test DELETE /schedule/<id> deletes schedule"""
    for schedule in example_schedules:
        response = client.delete(f'/schedule/{schedule["id"]}')
        assert response.status_code == 200
        assert response.json == {'success': True}
    response = client.delete('/schedule/999')
    assert response.status_code == 200
    assert response.json == {'success': False}

def test_archive_schedule(client):
    """Test POST /schedule/archive/<id> archives schedule"""
    response = client.post('/schedule/archive/1')
    assert response.status_code == 200
    assert response.json == {'success': True}

    response = client.post('/schedule/archive/999')
    assert response.status_code == 200
    assert response.json == {'success': False}

def test_get_reminders(client):
    """Test GET /schedule/remind returns reminder IDs"""
    response = client.get('/schedule/remind')
    assert response.status_code == 200
    assert response.json == {'schedule_id_list': [1, 2, 3]}

def test_sync_schedules(client):
    """Test GET /schedule/sync syncs schedules"""
    test_data = {'info': [
        {'id': 1, 'timestamp': datetime.now().isoformat()},
        {'id': 2, 'timestamp': datetime.now().isoformat()},
    ]}
    response = client.get('/schedule/sync', json=test_data)
    assert response.status_code == 200
    assert response.json == {'schedules': [example_schedules[0], example_schedules[1]]}

def test_invalid_method(client):
    """Test invalid methods return 405"""
    response = client.patch('/schedule/1')
    assert response.status_code == 405
    assert response.json == None