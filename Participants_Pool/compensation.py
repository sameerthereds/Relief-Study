import pandas as pd
import pickle
# Load the CSV files
weekly_survey = pd.read_csv('/home/sneupane/relief_study/data/qualtrics_data/Relief Weekly Survey (Processed).csv')
memories = pd.read_csv('/home/sneupane/relief_study/data/csv_files/stressors.csv')
with open("/home/sneupane/relief_study/data/Participants_Pool/active_users.pickle", "rb") as file:
        participant_hashmap = pickle.load(file)

weekly_survey = (
    weekly_survey.sort_values(by=["user_uuid", "week", "EndDate"], ascending=[True, True, False])
    .drop_duplicates(subset=["user_uuid", "week"], keep="first")
    .sort_index()  # Optional: to restore the original row order
)   

# Count the number of records for each user in the weekly survey
weekly_survey_count = weekly_survey['user_email'].value_counts().to_dict()
print(weekly_survey_count)
# Count the number of records for each user in the memories file
memories['user_email'] = memories['sender'].str.extract(r'<(.*?)>')


memories = (
    memories.sort_values(by=["user_email", "week"], ascending=[True, True])
    .drop_duplicates(subset=["user_email", "week"], keep="first")
    .sort_index()  # Optional: to restore the original row order
)   

memories_count = memories['user_email'].value_counts().to_dict()
print(memories_count)
# Create a dictionary for the cumulative total number of records for each user
cumulative_count = {}

# For each user, calculate the cumulative count by adding the counts from both surveys
# for user_id in set(weekly_survey['user_email']).union(set(memories['user_email'])):
for user_id in participant_hashmap:
    weekly_count = weekly_survey_count.get(user_id, 0)  # Get count from weekly survey, default to 0 if not present
    memory_count = memories_count.get(user_id, 0)      # Get count from memories, default to 0 if not present
    cumulative_count[user_id] = weekly_count + memory_count

# Print dictionaries to check the result
print("Weekly Survey Count Dictionary:", weekly_survey_count)
print("Memories Count Dictionary:", memories_count)
print("Cumulative Count Dictionary:", cumulative_count)


with open("/home/sneupane/relief_study/data/Participants_Pool/weekly_survey_count.pickle", "wb") as file:
        pickle.dump(weekly_survey_count, file)



with open("/home/sneupane/relief_study/data/Participants_Pool/memories_count.pickle", "wb") as file:
        pickle.dump(memories_count, file)


with open("/home/sneupane/relief_study/data/Participants_Pool/cumulative_count.pickle", "wb") as file:
        pickle.dump(cumulative_count, file)
