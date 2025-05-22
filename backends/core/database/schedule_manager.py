# Class to Manage the Schedules
# This class is inherited from the Database class and is responsible for managing schedules.

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from database import Database

class ScheduleManager(Database):
    def __init__(self, app=None):
        super().__init__()
        if app is not None:
            self.init_app(app)

    def init_app(self, app, auth=None):
        """Initialize the ScheduleManager with the given app.
        """
        self.settings = app.config.get('SCHEDULEMANAGER_SETTINGS', {})
        Database.init_app(self, app)
        if auth is not None:
            self.login(auth)
        
        
    def read_schedules(self) -> dict:
        """Read all schedules from the JSON file.
        Returns:
            list: The schedules read from the file.
        """
        return self.__file.get('schedules', [])
    
    def write_schedule(self, schedule: dict) -> bool:
        """Write a new schedule to the JSON file.
        Args:
            schedule (dict): The schedule to be written.
        Returns:
            bool: True if the write operation was successful, False otherwise.
        """
        if not isinstance(schedule, dict):
            raise ValueError("Schedule must be a dictionary.")
        if 'schedules' not in schedule:
            raise ValueError("Schedule must contain 'schedules' key.")
        if len(schedule['schedules']) != 1:
            raise ValueError("Schedule must contain exactly one schedule.")
        self.__file['schedules'].extend(schedule['schedules'])
        return self.__file
    
    def read_schedule_by_id(self, schedule_id: int) -> dict | None:
        """Read a schedule by its ID.
        Args:
            schedule_id (int): The ID of the schedule.
        Returns:
            dict: The schedule with the given ID.
        """
        for schedule in self.__file['schedules']:
            if schedule['id'] == schedule_id:
                return schedule
        return None
    
    def update_schedule(self, schedule: dict) -> bool:
        """Update an existing schedule in the JSON file.
        Args:
            schedule (dict): The updated schedule information.
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        if not isinstance(schedule, dict):
            raise ValueError("Schedule must be a dictionary.")
        if 'schedules' not in schedule:
            raise ValueError("Schedule must contain 'schedules' key.")
        if len(schedule['schedules']) != 1:
            raise ValueError("Schedule must contain exactly one schedule.")
        
        for i, s in enumerate(self.__file['schedules']):
            if s['id'] == schedule['schedules'][0]['id']:
                self.__file['schedules'][i] = schedule['schedules'][0]
                return True
        return False
    
    def delete_schedule(self, schedule_id: int) -> bool:
        """Delete a schedule by its ID.
        Args:
            schedule_id (int): The ID of the schedule to delete.
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        for i, schedule in enumerate(self.__file['schedules']):
            if schedule['id'] == schedule_id:
                del self.__file['schedules'][i]
                return True
        return False
    
    def archive_schedule(self, schedule_id: int) -> bool:
        """Archive a schedule by its ID.
        Args:
            schedule_id (int): The ID of the schedule to archive.
        Returns:
            bool: True if the archiving was successful, False otherwise.
        """
        for i, schedule in enumerate(self.__file['schedules']):
            if schedule['id'] == schedule_id:
                schedule['archived'] = True
                del self.__file['schedules'][i]
                if 'archived_schedules' not in self.__file:
                    self.__file['archived_schedules'] = []
                self.__file['archived_schedules'].append(schedule)
                return True
        return False
    
    def sync_schedules(self, schedules: List[Dict]) -> List[Dict]:
        """Synchronize the schedules with the JSON file.
        Args:
            schedules (List[Dict]): The list of schedules to synchronize.
        Returns:
            List[Dict]: The synchronized schedules.
        """
        # Compare the timestamps between every schedule the __file and the given schedules
        # If the timestamps are different, update the __file

        for schedule in schedules:
            for i, s in enumerate(self.__file['schedules']):
                if s['id'] == schedule['id']:
                    # Compare the timestamps in datetime format
                    time_s = datetime.strptime(s['timestamp'], '%Y-%m-%d %H:%M:%S')
                    time_schedule = datetime.strptime(schedule['timestamp'], '%Y-%m-%d %H:%M:%S')
                    if time_s < time_schedule:
                        self.__file['schedules'][i] = schedule
            else:
                self.__file['schedules'].append(schedule)
        
        return self.__file['schedules']
