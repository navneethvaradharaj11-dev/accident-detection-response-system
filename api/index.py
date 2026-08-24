from pathlib import Path
import sys

# Add root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from web_dashboard import DashboardRequestHandler

class handler(DashboardRequestHandler):
    pass
