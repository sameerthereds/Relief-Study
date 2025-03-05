import requests
import time
import zipfile
import io
from datetime import datetime

# Qualtrics API Details
API_TOKEN = ""  # Replace with your Qualtrics API Token
DATA_CENTER = ""  # Replace with your Data Center ID
SURVEY_ID = ""  # Replace with your Survey ID

# API URLs
BASE_URL = f"https://{DATA_CENTER}.qualtrics.com/API/v3"
EXPORT_URL = f"{BASE_URL}/surveys/{SURVEY_ID}/export-responses"

def export_qualtrics_data_csv():
    headers = {
        "Content-Type": "application/json",
        "X-API-TOKEN": API_TOKEN,
    }

    # Step 1: Start the export process
    print("Starting the export...")
    response = requests.post(EXPORT_URL, headers=headers, json={"format": "csv","useLabels": True})
    response.raise_for_status()
    progress_id = response.json()["result"]["progressId"]

    # Step 2: Check export progress
    progress_status = ""
    while progress_status != "complete":
        print("Checking export progress...")
        time.sleep(2)  # Wait before checking progress
        progress_check_url = f"{EXPORT_URL}/{progress_id}"
        response = requests.get(progress_check_url, headers=headers)
        response.raise_for_status()
        progress_status = response.json()["result"]["status"]
        if progress_status == "failed":
            raise Exception("Export failed.")

    # Step 3: Download the file
    file_id = response.json()["result"]["fileId"]
    download_url = f"{EXPORT_URL}/{file_id}/file"
    print("Downloading the export file...")
    response = requests.get(download_url, headers=headers)
    response.raise_for_status()

    # Step 4: Extract the file
    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        zf.extractall("/home/sneupane/relief_study/data/qualtrics_data")
    print("Export complete. Data saved in the 'qualtrics_data' folder.")

if __name__ == "__main__":
    current_datetime = datetime.now()

    print(f"Current Date and Time: {current_datetime}") 
    export_qualtrics_data_csv()
