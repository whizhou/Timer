import pytest
import sys
from pathlib import Path

# Add the root directory to the system path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from app import create_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()