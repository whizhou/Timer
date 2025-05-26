# Data Management Class acting as a foundation for all database-related operations.
# This class is designed to be extended by other classes that require database functionality.
# Do not specifically write for flask framework
import json
from pathlib import Path

class Database:
    def __init__(self):
        self._auth = None  # Authentication object, type: str
        self._path = None  # Path to the data file, type: str
        self._file = None  # Cache for the file, type: dict
        self.settings = None  # Settings for the database, type: dict

    def login(self, auth) -> bool:
        """Login method to set the authentication.
        Args:
            auth: The authentication object or credentials.
        """
        if self._auth is not None:
            self.logout()

        self._auth = auth
        self._path = Path(self.settings.get('SCHEDULE_JSON_PATH')) / f'{auth}.json'

        if not self._path.exists():
            # Create the file if it doesn't exist
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self.write({'auth': auth, 'schedules': []})

        self._file = self.read()

        return True
    
    def logout(self) -> bool:
        """Logout method to clear the authentication.
        """
        if self._auth is None:
            return False
        
        self._auth = None
        
        # Write the current data to the file
        self.write(self._file)

        self._path = None
        self._file = None
        return True

    def read(self) -> dict:
        """Read data from the _file in JSON format.
        Returns:
            dict: The data read from the database.
        """
        try:
            with open(self._path, 'r') as file:
                data = json.load(file)
            return data
        except Exception as e:
            print(f"Error reading file: {e}")
            return {}

    def write(self, data: dict) -> bool:
        """Write data to the _file in JSON format.
        Args:
            data (dict): The data to be written to the database.
        Returns:
            bool: True if the write operation was successful, False otherwise.
        """
        try:
            with open(self._path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=True)
            return True
        except Exception as e:
            print(f"Error writing to file: {e}")
            return False
    
    def save(self) -> bool:
        """Save the current _file to disk.
        Returns:
            bool: True if the save operation was successful, False otherwise.
        """
        return self.write(self._file)

    def append(self, data: dict) -> bool:
        """Append data to the _file in JSON format.
        Args:
            data (dict): The data to be appended to the database.
        Returns:
            bool: True if the append operation was successful, False otherwise.
        """
        self._file.update(data)
        return True

    def delete(self) -> bool:
        """Delete the file 
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            self._path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
