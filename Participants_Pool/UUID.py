import uuid
import pandas as pd
import os,pickle

file_path = "/home/sneupane/relief_study/data/Participants_Pool/participants_details.pickle"

# Check if the file exists
if os.path.exists(file_path):
    # File exists: Read the file
    print(f"'{file_path}' exists. Reading its contents...")
    with open(file_path, "rb") as file:
        data = pickle.load(file)
        print(f"Data read from the file: {data}")
else:
    # File does not exist: Create and save initial data
    print(f"'{file_path}' does not exist. Creating it with initial data...")
    data = {} # Initial data
    with open(file_path, "wb") as file:
        pickle.dump(data, file)
    print(f"Data saved to '{file_path}'.")

participants_details=pd.read_csv("/home/sneupane/relief_study/data/Participants_Pool/participants.csv")
# print(participants_details)

participant_start_date=pd.read_csv("/home/sneupane/relief_study/data/Participants_Pool/participant_start_date.csv")
# print(participant_start_date)

all_start_date=dict(zip(participant_start_date["email_id"],participant_start_date["start_date"]))
# print(all_start_date)
for index,row in participants_details.iterrows():
    # print(row)
    email_id=row["email_id"]
    name=row["Name"]
    new_uuid=str(uuid.uuid4())
    
    if email_id in data:
        old_uuid=data[email_id][0]
        flag=1
        data[email_id]=[old_uuid,name,all_start_date[email_id],flag]
    else:
        data[email_id]=[new_uuid,name,"No start date",1]

with open(file_path, "wb") as file:
        pickle.dump(data, file)
# print(f"Data saved to '{file_path}'.")
