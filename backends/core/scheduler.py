import json
import os
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict


class Scheduler:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        
        ###############################################################################
        # Test code
        ROOT_DIR = Path(__file__).resolve().parent.parent
        example_schedules_path = ROOT_DIR / 'data' / 'example_schedules.json'
        example_schedules = json.loads(example_schedules_path.read_text(encoding='utf-8'))
        self.example_schedules = example_schedules
        ###############################################################################

    def init_app(self, app):
        """Initialize the Scheduler with the given app."""
        self.settings = app.config.get('SCHEDULER_SETTINGS', {})

    def get_schedules(self) -> Dict:
        """Get the schedules from the JSON file.
        Returns:
            dict: A dictionary containing the schedules.
        Example:
            {
                "schedules": [
                    {
                        "id": 1,
                        "timestamp": 
                    },
                    {
                        "id": 2,
                        "title": "Schedule 2",
                        "content": "Content of schedule 2",
                        "timestamp": "2023-10-02T12:00:00Z"
                    }
                ]
            }
        """
        ###############################################################################
        # Test code
        return self.example_schedules
        ###############################################################################

    def create_schedule(self, schedule: dict) -> int:
        """Create a schedule based on the provided content.
        Args:
            schedule (dict): Include the content of the schedule and additional information.
        Returns:
            int: The ID of the created schedule or -1 if creation failed.
        """
        return -1

    def get_schedule_by_id(self, schedule_id: int) -> Dict | None:
        """Get a schedule by its ID.
        Args:
            schedule_id (int): The ID of the schedule.
        Returns:
            dict: The schedule with the given ID.
        """
        ###############################################################################
        # Test code
        for schedule in self.example_schedules['schedules']:
            if schedule['id'] == schedule_id:
                return schedule
        return None
        ###############################################################################

    def update_schedule(self, schedule: dict) -> bool:
        """Update a schedule by its ID.
        Args:
            schedule (dict): The updated schedule information.
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        ###############################################################################
        # Test code
        if 'id' not in schedule:
            return False
        return self.get_schedule_by_id(schedule['id']) is not None
        ###############################################################################

    def delete_schedule(self, schedule_id: int) -> bool:
        """Delete a schedule by its ID.
        Args:
            schedule_id (int): The ID of the schedule to delete.
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        ###############################################################################
        # Test code
        if schedule_id < 0:
            return False
        return self.get_schedule_by_id(schedule_id) is not None
        ###############################################################################



    def archive_schedule(self, schedule_id: int) -> bool:
        """Archive a schedule by its ID.
        Args:
            schedule_id (int): The ID of the schedule to archive.
        Returns:
            bool: True if the archiving was successful, False otherwise.
        """
        ###############################################################################
        # Test code
        if schedule_id < 0:
            return False
        return self.get_schedule_by_id(schedule_id) is not None
        ###############################################################################


    def get_reminders(self) -> List[int]:
        """Get reminders from the JSON file.
        Returns:
            list[int]: A list containing the id of the schedules that need reminders.
        """
        ###############################################################################
        # Test code
        return [schedule['id'] for schedule in self.example_schedules['schedules']]
        ###############################################################################

    def sync_schedules(self, info: List[Dict]) -> List[Dict]:
        """Synchronize the schedules with the JSON file.
        Args:
            info (List[Dict]): A list of dictionaries containing the schedule information.
                id (int): The ID of the schedules.
                timestamp (str): The timestamp of the schedules.
        Returns:
            List[Dict]: A list of dictionaries containing the schedules needing synchronization.
        """
        ###############################################################################
        # Test code
        return [schedule for schedule in self.example_schedules['schedules'] if schedule['id'] in [i['id'] for i in info]]
        ###############################################################################

# Create a global object for Scheduler
scheduler = Scheduler()