# Class to Manage the Schedules
# This class is inherited from the Database class and is responsible for managing schedules.

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta

from .database import Database

class ScheduleManager(Database):
    def __init__(self, app=None):
        super().__init__()
        if app is not None:
            self.init_app(app)
    
    def __del__(self):
        """Destructor to clean up resources."""
        # print("ScheduleManager instance is being deleted.")
        # self.logout()

    def init_app(self, app, auth=None):
        """Initialize the ScheduleManager with the given app.
        """
        self.settings = app.config.get('SCHEDULEMANAGER_SETTINGS', {})
        # print(f"ScheduleManager initialized with settings: {self.settings}")
        # Database.init_app(self, app)
        if auth is not None:
            self.login(auth)
        elif app.config.get('MODE') == 'development':
            self.login('dev')
        elif app.config.get('MODE') == 'testing':
            self.login('test')
        elif app.config.get('MODE') == 'default':
            self.login('default')
        
        
    def read_schedules(self) -> List[Dict]:
        """Read all schedules from the JSON file.
        Returns:
            list: The schedules read from the file.
        """
        return self._file.get('schedules', [])
    

    def write_schedule(self, schedule: dict) -> bool:
        """Write a new schedule to the JSON file.
        Args:
            schedule (dict): The schedule to be written.
        Returns:
            bool: True if the write operation was successful, False otherwise.
        """
        assert isinstance(schedule, dict), "Schedule must be a dictionary."
        assert 'id' in schedule, "Schedule must have an 'id' key."
        
        self._file['schedules'].extend(schedule)
        self.write(self._file)  # Write the updated file to disk

        return True
    
    def read_schedule_by_id(self, schedule_id: int) -> dict | None:
        """Read a schedule by its ID.
        Args:
            schedule_id (int): The ID of the schedule.
        Returns:
            dict: The schedule with the given ID.
        """
        for schedule in self._file['schedules']:
            if schedule['id'] == schedule_id:
                return schedule
        return None
    
    def create_schedule(self, schedules: List[Dict]) -> List[int]:
        """Create a new schedule based on the provided content.
        Args:
            schedule (dict): The content of the schedule and additional information.
        Returns:
            int: The ID of the created schedule or -1 if creation failed.
        """
        assert isinstance(schedules, list), "Schedules must be a list of dictionaries."

        created_ids = []
        for sched in schedules:

            if 'id' not in sched or sched['id'] == -1:
                # If no ID is provided, generate a new ID
                new_id = max([s['id'] for s in self._file['schedules']], default=0) + 1
                sched['id'] = new_id

            if 'timestamp' not in sched or sched['timestamp'] is None:
                # If no timestamp is provided, set it to the current time
                sched['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            self._file['schedules'].append(sched)
            created_ids.append(sched['id'])

        self.write(self._file)  # Write the updated file to disk

        return created_ids
        
    def update_schedule(self, schedule: dict) -> bool:
        """Update an existing schedule in the JSON file.
        This method will cover the file with the provided schedule.
        Args:
            schedule (dict): The updated schedule information.
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        assert isinstance(schedule, dict), "Schedule must be a dictionary."
        assert 'id' in schedule, "Schedule must have an 'id' key."
        
        if 'timestamp' not in schedule:
            schedule['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for i, s in enumerate(self._file['schedules']):
            if s['id'] == schedule['id']:
                self._file['schedules'][i] = schedule
                return True
        # else:
        #     # If the schedule ID is not found, create a new schedule
        #     self.create_schedule([schedule])
        #     return True
        return False
    
    def delete_schedule(self, schedule_id: int) -> bool:
        """Delete a schedule by its ID.
        Args:
            schedule_id (int): The ID of the schedule to delete.
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        for i, schedule in enumerate(self._file['schedules']):
            if schedule['id'] == schedule_id:
                del self._file['schedules'][i]
                return True
        return False
    
    def archive_schedule(self, schedule_id: int) -> bool:
        """Archive a schedule by its ID.
        Args:
            schedule_id (int): The ID of the schedule to archive.
        Returns:
            bool: True if the archiving was successful, False otherwise.
        """
        for i, schedule in enumerate(self._file['schedules']):
            if schedule['id'] == schedule_id:
                schedule['archived'] = True
                schedule['archived_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                del self._file['schedules'][i]

                if 'archived_schedules' not in self._file:
                    self._file['archived_schedules'] = []
                self._file['archived_schedules'].append(schedule)
                return True
        return False
    
    def get_remind_start(self) -> List[Dict]:
        """Get reminders from the JSON file.
        Returns:
            List[Dict]: The list of schedules that need to be reminded.
        """
        reminders = []
        for schedule in self._file['schedules']:
            if 'remind_start' in schedule:
                remind_start = ' '.join(schedule['remind_start']).strip()
                remind_start = datetime.strptime(remind_start, '%Y-%m-%d %H:%M:%S')
                if remind_start < datetime.now():
                    reminders.append(schedule)
        return reminders
    
    def get_remind_before(self) -> List[Dict]:
        """Get schedules that are becoming active.
        Returns:
            List[Dict]: The list of schedules that are becoming active.
        """
        incoming_schedules = []
        for schedule in self._file['schedules']:
            if 'remind_before' in schedule:
                begin_time = ' '.join(schedule['begin_time']).strip()
                begin_time = datetime.strptime(begin_time, '%Y-%m-%d %H:%M:%S')
                remind_before = schedule.get('remind_before', 0)
                # remind_before is the time (in minutes) to remind before the schedule starts (optional)
                remind_start = begin_time - timedelta(minutes=remind_before)
                if remind_start < datetime.now():
                    incoming_schedules.append(schedule)

        return incoming_schedules
    
    def sync_schedules(self, schedules: List[Dict]) -> List[Dict]:
        """Synchronize the schedules with the JSON file.
        Args:
            schedules (List[Dict]): The list of schedules to synchronize.
        Returns:
            List[Dict]: The synchronized schedules.
        """
        # Compare the timestamps between every schedule the _file and the given schedules
        # If the timestamps are different, update the _file
        assert isinstance(schedules, list), "Schedules must be a list of dictionaries."

        for schedule in schedules:
            if schedule['id'] == -1:
                # If the schedule ID is -1, it means it's a new schedule
                # Generate a new ID for the schedule
                self.create_schedule([schedule])
            else:
                for i, s in enumerate(self._file['schedules']):
                    if s['id'] == schedule['id']:
                        # Compare the timestamps in datetime format
                        time_s = datetime.strptime(s['timestamp'], '%Y-%m-%d %H:%M:%S')
                        time_schedule = datetime.strptime(schedule['timestamp'], '%Y-%m-%d %H:%M:%S')
                        if time_s < time_schedule:
                            self._file['schedules'][i] = schedule
                        break
                else:
                    # If the schedule ID is not found, create a new schedule
                    self.create_schedule([schedule])
        
        return self._file['schedules']
    
    def save_cache(self) -> bool:
        """Save the current state of the schedules to the JSON file.
        Returns:
            bool: True if the save operation was successful, False otherwise.
        """
        try:
            self.save()
            return True
        except Exception as e:
            print(f"Error saving schedules: {e}")
            return False
        
    def get_schedule_quantity(self) -> int:
        """Get the total number of schedules.
        Returns:
            int: The total number of schedules.
        """
        return len(self._file.get('schedules', []))

