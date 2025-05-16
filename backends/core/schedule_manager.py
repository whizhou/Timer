# Class to Manage the Schedules

class ScheduleManager:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the ScheduleManager with the given app.
        """
        self.settings = app.config.get('SCHEDULEMANAGER_SETTINGS', {})

    