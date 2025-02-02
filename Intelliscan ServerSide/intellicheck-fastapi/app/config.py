import os
from decouple import config  # Use environment variables for flexibility

# Get the home directory (cross-platform)
HOME_DIR = os.path.expanduser("~")

# Use environment variables or fallback to default directories
UPLOAD_DIRECTORY = config("UPLOAD_DIRECTORY", default=os.path.join(HOME_DIR, "uploaded_files"))
REPORT_DIRECTORY = config("REPORT_DIRECTORY", default=os.path.join(HOME_DIR, "reports"))

# Ensure directories exist
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
os.makedirs(REPORT_DIRECTORY, exist_ok=True)

print("Upload Directory:", UPLOAD_DIRECTORY)
print("Report Directory:", REPORT_DIRECTORY)
