from .scheduler import Scheduler
from .ai_scheduler import AIScheduler
from .auth_manager import AuthManager

# Create a global object for Scheduler
# scheduler = Scheduler()
scheduler = AIScheduler()

auth_manager = AuthManager()
