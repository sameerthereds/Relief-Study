import pandas as pd
import re
# Load the first CSV (user_id and date of entry)
first_csv = pd.read_csv("/home/sneupane/relief_study/data/csv_files/extracted_stressor_location.csv")

# Parse email_id from user_id column
first_csv['email_id'] = first_csv['sender'].apply(lambda x: re.search(r'<(.*?)>', x).group(1) if re.search(r'<(.*?)>', x) else None)

# Load the second CSV (to be updated)
second_csv = pd.read_csv("/home/sneupane/relief_study/data/Participants_Pool/participants.csv")

# Convert the date column to datetime format in case it's not
first_csv['date_of_entry'] = pd.to_datetime(first_csv['date']).dt.date

# Find the first date for each user
first_date_per_user = first_csv.groupby('email_id')['date_of_entry'].min().reset_index()

# Merge the first_date_per_user with the second CSV on user_id
updated_second_csv = second_csv.merge(first_date_per_user, on='email_id', how='left')

# Update the 'start_date' column with the first date
updated_second_csv['start_date'] = updated_second_csv['date_of_entry']

# Drop the extra date_of_entry column (optional)
updated_second_csv = updated_second_csv.drop(columns=['date_of_entry','flag'])
updated_second_csv["start_date"]=updated_second_csv["start_date"].fillna("No Start Date")

# Save the updated second CSV
updated_second_csv.to_csv('/home/sneupane/relief_study/data/Participants_Pool/participant_start_date.csv', index=False)

# print("The start_date column has been updated.")