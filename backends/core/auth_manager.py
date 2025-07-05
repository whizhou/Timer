import json
import os
from typing import Dict, List
from pathlib import Path

class AuthManager:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._path = Path(app.config.get('AUTH_JSON_PATH')).resolve()
        if not self._path.exists():
            self._path.mkdir(parents=True, exist_ok=True)
        
        self._file_path = self._path / 'auth.json'
        if not self._file_path.exists():
            self._file_path.write_text('{"users": []}', encoding='utf-8')
        
    def add_user(self, username: str, password: str) -> None:
        """Add a new user with the given username and password."""
        users = self._load_users()
        if any(user['username'] == username for user in users):
            raise ValueError(f"User '{username}' already exists.")
    
        user_id = len(users) + 1  # Simple user ID generation
        
        users.append({'username': username, 'password': password, 'id': user_id})
        self._save_users(users)

    def remove_user(self, username: str) -> None:
        """Remove a user with the given username."""
        users = self._load_users()
        users = [user for user in users if user['username'] != username]
        self._save_users(users)

    def authenticate(self, username: str, password: str) -> Dict | None:
        """Authenticate a user with the given username and password."""
        users = self._load_users()
        user = None
        error = None
        for u in users:
            if u['username'] == username:
                user = u
                if user['password'] != password:
                    error = f"Incorrect password for user '{username}'."
                break

        if not user:
            error = f"User '{username}' not found."
        
        if error:
            raise ValueError(error)
        
        return user

    def _load_users(self) -> list[dict]:
        """Load users from the JSON file."""
        try:
            with open(self._file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data.get('users', [])
        except Exception as e:
            print(f"Error loading users: {e}")
            return []

    def _save_users(self, users: list[dict]) -> None:
        """Save users to the JSON file."""
        try:
            with open(self._file_path, 'w', encoding='utf-8') as file:
                json.dump({'users': users}, file, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
