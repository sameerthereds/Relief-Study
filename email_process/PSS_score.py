import pandas as pd

# Hashmap of questions to their respective columns
questions_map = {
    "In the last week, how often have you been upset because of something that happened unexpectedly?": "q1",
    "In the last week, how often have you felt that you were unable to control the important things in your life?": "q2",
    "In the last week, how often have you felt nervous and 'stressed'?": "q3",
    "In the last week, how often have you felt confident about your ability to handle your personal problems?": "q4",  # Reverse scored
    "In the last week, how often have you felt that things were going your way?": "q5",  # Reverse scored
    "In the last week, how often have you found that you could not cope with all the things you had to do?": "q6",
    "In the last week, how often have you been able to control irritations in your life?": "q7",  # Reverse scored
    "In the last week, how often have you felt that you were on top of things?": "q8",  # Reverse scored
    "In the last week, how often have you been angered because of things that were outside of your control?": "q9",
    "In the last week, how often have you felt difficulties were piling up so high that you could not overcome them?": "q10",
}

# Sample DataFrame (replace with your actual dataset)
data = {
    "q1": [2, 3, 4],
    "q2": [1, 3, 2],
    "q3": [3, 2, 1],
    "q4": [4, 2, 1],  # Reverse scoring
    "q5": [2, 3, 4],  # Reverse scoring
    "q6": [3, 2, 1],
    "q7": [1, 4, 3],  # Reverse scoring
    "q8": [3, 2, 4],  # Reverse scoring
    "q9": [2, 1, 3],
    "q10": [4, 3, 2],
}

# Create DataFrame
df = pd.DataFrame(data)

# Questions to reverse score (mapped from the hashmap)
reverse_columns = [questions_map[q] for q in questions_map if "Reverse scored" in q]

# Reverse scoring function
def reverse_score(value):
    """Reverse scores: 0 -> 4, 1 -> 3, 2 -> 2, 3 -> 1, 4 -> 0."""
    return 4 - value

# Apply reverse scoring
for col in reverse_columns:
    df[col] = df[col].apply(reverse_score)

# Calculate total PSS score
df["PSS_Total"] = df.sum(axis=1)

# Classification function
def classify_stress_PSS(score):
    """Classify stress levels based on the total PSS score."""
    if 0 <= score <= 13:
        return "Low Stress"
    elif 14 <= score <= 26:
        return "Moderate Stress"
    elif 27 <= score <= 40:
        return "High Stress"
    else:
        return "Invalid Score"

# Classify stress levels
df["Stress_Level"] = df["PSS_Total"].apply(classify_stress_PSS)

# Display results
print(df)