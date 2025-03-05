import pickle
import pandas as pd
with open("/home/sneupane/relief_study/data/Participants_Pool/participants_details.pickle", "rb") as file:
        participants_details = pickle.load(file)



completed_users=[""]
withdrawn_users=[""]

active_users={}
for user in participants_details:
    
    if user not in completed_users:
        if user not in withdrawn_users:
             if participants_details[user][2]!="No Start Date":
                 active_users[user]=participants_details[user]


with open("/home/sneupane/relief_study/data/Participants_Pool/active_users.pickle", "wb") as file:
        pickle.dump(active_users, file)