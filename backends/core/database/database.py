# Data Management Class acting as a foundation for all database-related operations.
# This class is designed to be extended by other classes that require database functionality.
# Do not specifically write for flask framework
import json
from pathlib import Path

class Database:
    def __init__(self):
        self.__auth = None  # Authentication object, type: str
        self.__path = None  # Path to the data file, type: str
        self.__file = None  # Cache for the file, type: dict
        self.settings = None  # Settings for the database, type: dict

    def login(self, auth) -> bool:
        """Login method to set the authentication.
        Args:
            auth: The authentication object or credentials.
        """
        self.__auth = auth
        self.__path = Path(self.settings.get('DATA_PATH')) / f'{auth}.json'

        if not self.__path.exists():
            # Create the file if it doesn't exist
            self.__path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.__path, 'w') as file:
                json.dump({'shedules': []}, file)
        
        self.__file = self.read()

        return True
    
    def logout(self) -> bool:
        """Logout method to clear the authentication.
        """
        self.__auth = None
        
        # Write the current data to the file
        self.write(self.__file)

        self.__path = None
        self.__file = None
        return True

    def read(self) -> dict:
        """Read data from the __file in JSON format.
        Returns:
            dict: The data read from the database.
        """
        try:
            with open(self.__path, 'r') as file:
                data = json.load(file)
            return data
        except Exception as e:
            print(f"Error reading file: {e}")
            return {}

    def write(self, data: dict) -> bool:
        """Write data to the __file in JSON format.
        Args:
            data (dict): The data to be written to the database.
        Returns:
            bool: True if the write operation was successful, False otherwise.
        """
        try:
            with open(self.__path, 'w') as file:
                json.dump(data, file)
            return True
        except Exception as e:
            print(f"Error writing to file: {e}")
            return False
    
    def append(self, data: dict) -> bool:
        """Append data to the __file in JSON format.
        Args:
            data (dict): The data to be appended to the database.
        Returns:
            bool: True if the append operation was successful, False otherwise.
        """
        self.__file.update(data)
        return True

    def delete(self) -> bool:
        """Delete the file 
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            self.__path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
