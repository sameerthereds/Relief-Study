import pandas as pd
import uuid
import pandas as pd
import os,pickle
from datetime import datetime

screening_csv=pd.read_csv("/home/sneupane/relief_study/data/qualtrics_data/RELIEF Screening Form.csv")[2:]
# print(screening_csv.head(2))
# print(screening_csv.columns)
# print(screening_csv[[ 'Q19', 'Q20', 'Q21','Q22', 'Q23','Q24','Q25']])
columns_questions=[ 'Q25','Q24', 'Q23','Q19', 'Q20', 'Q21','Q22',]
# print(screening_csv[columns_questions])



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


# print(participants_details)

for index,row in screening_csv.iterrows():
    email_id=row["Q25"]
    name=row["Q24"]
    # date=row["start_date"]
    occupation=row["Q23"]
    gender=row["Q19"]
    age=row["Q20"]
    race=row["Q21"]
    eth=row["Q22"]
    # date=datetime.strptime(date, "%Y-%m-%d")
    
  
    if email_id in data:
        old_uuid=data[email_id][0]
        data[email_id]=[old_uuid,name,occupation,gender,age,race,eth]
    else:
        new_uuid=str(uuid.uuid4())
        data[email_id]=[new_uuid,name,occupation,gender,age,race,eth]
    
with open(file_path, "wb") as file:
        pickle.dump(data, file)
# print(f"Data saved to '{file_path}'.")
current_datetime = datetime.now()
print(f"Current Date and Time: {current_datetime}")
print("Process Done")