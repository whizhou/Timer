import json
import os
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

from .database.schedule_manager import ScheduleManager


class Scheduler:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the Scheduler with the given app."""
        self.settings = app.config.get('SCHEDULER_SETTINGS', {})
        self.manager = ScheduleManager(app)

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
        schedules = self.manager.read_schedules()
        return {'schedules': schedules}

    def create_schedule(self, schedules: List[Dict]) -> List[int]:
        """Create a schedule based on the provided content.
        Args:
            schedules (List[Dict]): A list of schedules to be created.
        Returns:
            List[int]: The IDs of the created schedules, -1 if creation failed.
        """
        return self.manager.create_schedule(schedules)

    def get_schedule_by_id(self, schedule_id: int) -> Dict | None:
        """Get a schedule by its ID.
        Args:
            schedule_id (int): The ID of the schedule.
        Returns:
            dict: The schedule with the given ID.
        """
        return self.manager.read_schedule_by_id(schedule_id)

    def update_schedule(self, schedules: List[Dict]) -> bool:
        """Update a schedule by its ID.
        Args:
            schedules (List[Dict]): A list of schedules to be updated.
        Returns:
            bool: True if all updates were successful, False otherwise.
        """
        success = []
        for schedule in schedules:
            success.append(self.manager.update_schedule(schedule))
        return all(success)

    def delete_schedule(self, schedule_id: int) -> bool:
        """Delete a schedule by its ID.
        Args:
            schedule_id (int): The ID of the schedule to delete.
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return self.manager.delete_schedule(schedule_id)



    def archive_schedule(self, schedule_id: int) -> bool:
        """Archive a schedule by its ID.
        Args:
            schedule_id (int): The ID of the schedule to archive.
        Returns:
            bool: True if the archiving was successful, False otherwise.
        """
        return self.manager.archive_schedule(schedule_id)


    def get_reminders(self) -> List[int]:
        """Get reminders from the JSON file, the schedules' remider_start time is in the past.
        Returns:
            List[Dict]: List of schedules that need to be reminded.
        """
        return self.manager.get_reminders()

    def get_incoming_schedules(self) -> List[Dict]:
        """Get schedules that are about to be reminded.
        Returns:
            List[Dict]: List of schedules that are about to be reminded.
        """
        return self.manager.get_incoming_schedules()

    def sync_schedules(self, schedules: List[Dict]) -> List[Dict]:
        """Synchronize the schedules with the JSON file.
        Args:
            schedules (List[Dict]): All schedules to be synchronized.
        Returns:
            List[Dict]: The synchronized schedules.
        """
        return self.manager.sync_schedules(schedules)
    
    def save(self) -> bool:
        """Save the current cache to the JSON file.
        Returns:
            bool: True if the save operation was successful, False otherwise.
        """
        return self.manager.save_cache()
