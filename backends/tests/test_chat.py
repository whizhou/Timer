import pytest
import json
from flask import jsonify
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

@pytest.fixture
def client(app):
    """Fixture for Flask test client"""
    return app.test_client()

def test_multi_chat(client):
    """Test multi-chat"""
    # Test with multiple messages
    messages = [

       "创建日程：明天下午3点开会，会议内容为讨论项目进展",
       "修改日程：明天下午3点的会议改为后天上午10点",
    #    "明天上午的会议取消"

    ]
    
    for message in messages:
        response = client.post('/chat/', json={'message': message})
        assert response.status_code == 200
        assert 'messages' in response.json
        assert 'response' in response.json
        assert 'schedule' in response.json

        # Use `pytest -s` to see the print output
        print(f"\nMessage: {message}")
        print(f"Response: {response.json['response']}")
    
    # print(f"\nAll chat messages: \n{response.json['messages']}")
