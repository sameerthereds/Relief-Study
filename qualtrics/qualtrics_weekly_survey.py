import requests
import time
import zipfile
import io
import pandas as pd
from datetime import datetime


# Qualtrics API Details
API_TOKEN = ""  # Replace with your Qualtrics API Token
DATA_CENTER = ""  # Replace with your Data Center ID
SURVEY_ID = ""  # Replace with your Survey ID

# API URLs
BASE_URL = f"https://{DATA_CENTER}.qualtrics.com/API/v3"
EXPORT_URL = f"{BASE_URL}/surveys/{SURVEY_ID}/export-responses"

answers_map={"0 - never":0,
             "1 - almost never":1,
             "2- sometimes":2,
             "3 - fairly often":3,
             "4 - very often":4            

}

# PSS 10
# questions_map = {
#     "In the last week, how often have you been upset because of something that happened unexpectedly?": "Q4_1",
#     "In the last week, how often have you felt that you were unable to control the important things in your life?": "Q4_2",
#     "In the last week, how often have you felt nervous and 'stressed'?": "Q4_3",
#     "In the last week, how often have you felt confident about your ability to handle your personal problems?": "Q4_4",  # Reverse scored
#     "In the last week, how often have you felt that things were going your way?": "Q4_5",  # Reverse scored
#     "In the last week, how often have you found that you could not cope with all the things you had to do?": "Q4_6",
#     "In the last week, how often have you been able to control irritations in your life?": "Q4_7",  # Reverse scored
#     "In the last week, how often have you felt that you were on top of things?": "Q4_8",  # Reverse scored
#     "In the last week, how often have you been angered because of things that were outside of your control?": "Q4_9",
#     "In the last week, how often have you felt difficulties were piling up so high that you could not overcome them?": "Q4_10"
# }

#PSS 
questions_map = {   
    "In the last week, how often have you felt that you were unable to control the important things in your life?": "Q4_1",    
    "In the last week, how often have you felt confident about your ability to handle your personal problems?": "Q4_2",  # Reverse scored
    "In the last week, how often have you felt that things were going your way?": "Q4_3",  # Reverse scored
    "In the last week, how often have you felt difficulties were piling up so high that you could not overcome them?": "Q4_4"
}

# Sample DataFrame (replace with your actual dataset)
# def classify_stress_PSS(score):
#     """Classify stress levels based on the total PSS score."""
#     if 0 <= score <= 13:
#         return "Low Stress"
#     elif 14 <= score <= 26:
#         return "Moderate Stress"
#     elif 27 <= score <= 40:
#         return "High Stress"
#     else:
#         return "Invalid Score"

def classify_stress_PSS(score):
    """Classify stress levels based on the total PSS score."""
    if 0 <= score <= 7:
        return "Average Stress"
    
    elif 8 <= score <= 16:
        return "High Stress"
    else:
        return "Invalid Score"


# def classify_score_DASS(row):
#     if row.isnull().any():
#         return None
#     total = row.sum()*2
#     # print(total)
#     if 0 <= total <= 14:
#         return "Normal"
#     elif 15 <= total <= 18:
#         return "Mild"
#     elif 19 <= total <= 25:
#         return "Moderate"
#     elif 26 <= total <= 33:
#         return "Severe"
#     else:  # 34+
#         return "Extremely Severe"

def reverse_score(value):
        """Reverse scores: 0 -> 4, 1 -> 3, 2 -> 2, 3 -> 1, 4 -> 0."""
        return 4 - value

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

    data = pd.read_csv("/home/sneupane/relief_study/data/qualtrics_data/Relief Weekly Survey.csv",skiprows=[ 1,2])
    # print(data.columns)
    
    # print(len(data))
    df = pd.DataFrame(data)
    # print(df.columns)
    # print(len(df))
    # print(df[["Finished","Status"]])
    df=df.loc[df["Finished"]==True]
    df=df.loc[df["Status"]=="IP Address"]
    # print(len(df))
    #PSS score
   
    # print(df["Q5_1"])
    columns_to_sum = ['Q5_1', 'Q5_2', 'Q5_3','Q5_4']
    reverse_columns = ['Q5_2', 'Q5_3']   
    for column in columns_to_sum:
        if column in df.columns:
            df[column] = df[column].map(answers_map).fillna(-1)
    # print(df[columns_to_sum])
    # print(reverse_columns)
    for col in reverse_columns:
        df[col] = df[col].apply(reverse_score)
    # print(df[columns_to_sum])
    df["Total"] = df[columns_to_sum].sum(axis=1)
    df["Classification"] = df["Total"].apply(classify_stress_PSS)

    
    # DAS Score
#     print(df.columns)

#     columns_to_sum = ['Q5_1', 'Q5_2', 'Q5_3', 'Q5_4', 'Q5_5', 'Q5_6', 'Q5_7',]
#     df[columns_to_sum] = df[columns_to_sum].apply(pd.to_numeric, errors="coerce")
#     print(df[columns_to_sum])
# # Sum the 7 columns and classify
#     df["Total"] = df[columns_to_sum].sum(axis=1)*2
#     df["Classification"] = df[columns_to_sum].apply(classify_score_DASS, axis=1)

    # print(df[["Total","Classification"]])
    df.to_csv("/home/sneupane/relief_study/data/qualtrics_data/Relief Weekly Survey.csv")
    print("Data Saved after Classification")
# Define a function to classify the scores


   

if __name__ == "__main__":
    current_datetime = datetime.now()

    print(f"Current Date and Time: {current_datetime}")
    export_qualtrics_data_csv()
