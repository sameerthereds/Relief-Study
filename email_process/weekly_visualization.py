import os
import pandas as pd
import matplotlib.pyplot as plt
from utils import *
from matplotlib.ticker import MaxNLocator
def filter_and_plot(data, user, current_week, output_folder):
    """
    Filters the data for the given user and week, creates subplots for weekly stress scores
    and stressors per day, and saves the figure in the user's folder.

    Args:
        data (pd.DataFrame): The dataset containing columns ['user_email', 'week', 'Total', 'Q6'].
        user (str): The user ID (email) to filter data for.
        current_week (int): The current week to filter data for.
        output_folder (str): The path to the folder where the image will be saved.
    """
    # Ensure no missing weeks for the user
    answer_map = {
        'Four or more times': 4,
        'More than twice but at most three times': 3,
        'More than once but at most twice': 2,
        'At most once': 1
    }
    # print(data["Q2"].unique())
    data['Q2'] = data['Q2'].map(answer_map).fillna(0) 

    user_data = data[data['user_email'] == user].copy()

    if user_data.empty:
        raise ValueError(f"No data found for user {user}")

    # Fill in missing weeks with default values
    all_weeks = pd.Series(range(1, current_week + 1), name="week")
    user_data = pd.merge(all_weeks, user_data, on="week", how="left")
    user_data["user_email"] = user  # Ensure user column is consistent
    user_data["EndDate"]=pd.to_datetime(user_data["EndDate"])
    # print(len(unprocessed_entries))
    user_data = (
    user_data.sort_values(by=["week", "EndDate"], ascending=[True, False])
    .drop_duplicates(subset=["week"], keep="first")
    .sort_index()  # Optional: to restore the original row order
)   

    user_data=user_data.loc[user_data["Classification"]!="Invalid Score"]
    user_data["Total"] = user_data["Total"].apply(lambda x: x if x >= 0 else None)
    missing_mask = user_data[['Total', 'Q2']].isna().any(axis=1)


    user_data["Total"] = user_data["Total"].fillna(0)
    user_data["Q2"] = user_data["Q2"].fillna(0)

    # print(user)
    # print(user_data[["week","Total","Q2"]])

    # print(missing_mask,user)
    # Extract data for plotting
    weeks = user_data["week"]
    scores = user_data["Total"]
    stressors = user_data["Q2"]

    # Create the user's folder if it doesn't exist
    user_folder = os.path.join(output_folder, user)
    os.makedirs(user_folder, exist_ok=True)

    # Set up the subplots
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    fig.tight_layout(pad=5.0)
    
    # Subplot 1: Weekly Stress Score
    ax[0].plot(weeks, scores, color='blue', linestyle='--', linewidth=2)
    ax[0].scatter(weeks[~missing_mask], scores[~missing_mask], color='blue', s=80, label="Available Data")
    ax[0].scatter(weeks[missing_mask], scores[missing_mask], color='blue', s=80, alpha=0.3, label="Missing Data")
    ax[0].set_title('Weekly Stress Score', fontsize=14, fontweight='bold')
    ax[0].set_xlabel('Week', fontsize=12)
    ax[0].set_xlim(0, 14)  # Set x-axis range from 1 to 14
    ax[0].set_ylabel('Stress Score', fontsize=12)
    ax[0].xaxis.set_major_locator(MaxNLocator(integer=True))  # Enforce integer x-axis
    ax[0].yaxis.set_major_locator(MaxNLocator(integer=True))
    ax[0].grid(True, linestyle='--', alpha=0.2)
    ax[0].legend()

    # Subplot 2: Stressors per Week
    ax[1].plot(weeks, stressors, color='green', linestyle='--', linewidth=2)
    ax[1].scatter(weeks[~missing_mask], stressors[~missing_mask], color='green', s=80, label="Available Data")
    ax[1].scatter(weeks[missing_mask], stressors[missing_mask], color='green', s=80, alpha=0.3, label="Missing Data")
    ax[1].set_title('Stressors per Week', fontsize=14, fontweight='bold')
    ax[1].set_xlabel('Week', fontsize=12)
    ax[1].set_ylim(-0.2,4)
    ax[1].set_xlim(0, 14)  # Set x-axis range from 1 to 14
    ax[1].set_ylabel('Number of Stressors', fontsize=12)
    ax[1].xaxis.set_major_locator(MaxNLocator(integer=True))  # Enforce integer x-axis
    ax[1].yaxis.set_major_locator(MaxNLocator(integer=True))
    ax[1].grid(True, linestyle='--', alpha=0.2)
    ax[1].legend()

    # Save the figure
    filename = f"{user}_week_{current_week}.png"
    output_path = os.path.join(user_folder, filename)
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Figure saved at {output_path}")
    return output_path

# Example usage
def create_visuals(flag):
    # Sample data
    if flag==True:
        data = pd.read_csv("/home/sneupane/relief_study/data/qualtrics_data/Relief Weekly Survey.csv")


        for user in participant_hashmap:
            user = user
            email_sent_date = datetime.now().date()
            current_week=user_days_week[user][0][email_sent_date]-1
            # current_week=6
            # for current_week in [1,2,3,4,5,6,7]:
            output_folder = "/home/sneupane/relief_study/data/weekly_graphs"
            current_week=current_week
            try:
                plot_path = filter_and_plot(data, user, current_week, output_folder)
                print(f"Plot ready at {plot_path}")
            except ValueError as e:
                print(e, user)

# create_visuals(True)