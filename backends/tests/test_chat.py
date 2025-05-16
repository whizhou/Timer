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
       "你好",
       "你是谁？"
    ]
    
    for message in messages:
        response = client.post('/chat/', json={'message': message})
        assert response.status_code == 200
        assert 'messages' in response.json
        assert 'response' in response.json

        # Use `pytest -s` to see the print output
        # print(f"\nResponse: {response.json['response']}")
    
    # print(f"\nAll chat messages: \n{response.json['messages']}")
