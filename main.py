import subprocess
import os

# Define the paths to the scripts in the utils folder
scraper_script = os.path.join('utils', 'scraper.py')
extract_meds_links_script = os.path.join('utils', 'extract_meds_links.py')
mongodb_connection_script = os.path.join('utils', 'mongodb_connection.py')
test_script = os.path.join('utils', 'test.py')

# Step 1: Run scraper.py
try:
    print("Running scraper.py...")
    subprocess.run(['python3', scraper_script], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error occurred while running scraper.py: {e}")
    exit(1)

# Step 2: Run extract_meds_links.py
try:
    print("Running extract_meds_links.py...")
    subprocess.run(['python3', extract_meds_links_script], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error occurred while running extract_meds_links.py: {e}")
    exit(1)

# Step 3: Run mongodb_connection.py
try:
    print("Running mongodb_connection.py...")
    subprocess.run(['python3', mongodb_connection_script], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error occurred while running mongodb_connection.py: {e}")
    exit(1)

# Step 4: Run test.py
try:
    print("Running test.py...")
    subprocess.run(['python3', test_script], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error occurred while running test.py: {e}")
    exit(1)
