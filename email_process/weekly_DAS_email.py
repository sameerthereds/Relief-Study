import pandas as pd
import smtplib,math
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from credentials import *
from weekly_visualization import *
from datetime import datetime

# Configuration
COLUMN_TO_PROCESS = ["Total","Classification"]  # Column name to include in the email
CSV_FILE_PATH = "/home/sneupane/relief_study/data/qualtrics_data/Relief Weekly Survey.csv"  # Path to the input CSV file
PROCESSED_CSV_FILE = "/home/sneupane/relief_study/data/qualtrics_data/Relief Weekly Survey (Processed).csv"  # Path to the tracking file
survey_sent_tracking_csv="/home/sneupane/relief_study/data/csv_files/email__DAS_tracking.csv"
current_datetime = datetime.now()


# Function to send an email
def send_email(to_email, name,final_score,classification,current_week):
    subject = "Weekly Summary"
    html_content = f"""
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; background-color: #f9f9f9; padding: 20px; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
            <!-- Header -->
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #007bff; font-size: 24px; margin: 0;">Your Stress and Stressor Profile</h1>
                <p style="font-size: 16px; margin: 10px 0 0;"></p>
            </div>
            
            <!-- Dynamic Image -->
            <div style="text-align: center; margin: 20px 0;">
                <img src="cid:stress_chart" alt="Stress Chart" style="max-width: 100%; height: auto; border-radius: 8px; border: 1px solid #ddd;"/>
            </div>

            <!-- Main Content -->
              <p style="font-size: 16px; color: #333;">Hi <strong>{name}</strong>,</p>
            <p style="font-size: 16px; color: #555; text-align: left;">
                <br>Your weekly stress score from weekly survey for week <strong>{int(current_week)}</strong> was <strong>{final_score}</strong>, which indicates <strong>{classification}</strong>.
            </p>

            <!-- Additional Information -->
            <p style="font-size: 16px; color: #555; text-align: left;">
                Thank you for your continued participation in the RELIEF Study.
            </p>
            <!-- Signature -->
            <p style="font-size: 16px; color: #333; text-align: left; margin-top: 30px;">
                Warm regards,
                <br><strong>The RELIEF Study Team</strong>
                <br><strong>The mDOT Center</strong>
                <br><strong>University of Memphis</strong>
            </p>
        </div>
    </body>
</html>
"""
    try:
        # Create the email message
        msg = MIMEMultipart("related")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach the HTML content
        msg.attach(MIMEText(html_content, "html"))

        # Embed the image
        with open("/home/sneupane/relief_study/data/weekly_graphs/"+to_email+"/"+to_email+"_week_"+str(int(current_week))+".png", "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header("Content-ID", "<stress_chart>")
            img.add_header("Content-Disposition", "inline", filename="weekly_Data.png")
            msg.attach(img)

        # Send the email
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
            server.login(EMAIL_ADDRESS, PASSWORD)
            server.send_message(msg)
            print(f"Email sent to {to_email}")
        log_email_sent(to_email, name, current_week, current_datetime)
      
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")
        return False


def is_email_sent(user_id, week, csv_file=survey_sent_tracking_csv):
    """
    Check if the email has already been sent to the user for the given week.

    Args:
        user_id (str): The unique identifier for the user.
        week (int): The week number to check.
        csv_file (str): The CSV file that stores email logs.

    Returns:
        bool: True if the email has already been sent, False otherwise.
    """
    try:
        print(user_id)
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # print(user_id,week)
                if row["User ID"] == user_id and int(float(row["Week"])) == int(week):
                    return True
    except FileNotFoundError:
        # File does not exist, so no emails have been logged yet
        return False
    return False

def log_email_sent(user_id, username, week, email_sent_date, csv_file=survey_sent_tracking_csv):
    """
    Log email information in a CSV file.

    Args:
        user_id (str): The unique identifier for the user.
        username (str): The username of the participant.
        week (int): The week number for which the email was sent.
        email_sent_date (datetime.date): The date when the email was sent.
        csv_file (str): The CSV file to store email logs.
    """
    # Write header if the file doesn't exist
    try:
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            file.seek(0, 2)  # Move to the end of the file
            if file.tell() == 0:  # If the file is empty, write the header
                writer.writerow(["User ID", "Username", "Week", "Email Sent Date"])
            # Log the email information
            writer.writerow([user_id, username, week, email_sent_date])
    except Exception as e:
        print(f"Error writing to CSV file: {e}")

# Main function
def process_csv():
    df = pd.read_csv(CSV_FILE_PATH)
    # df=df.loc[df["Finished"]=="True"]
    # df=df.loc[df["Status"]=="IP Address"]
    try:
        processed_df = pd.read_csv(PROCESSED_CSV_FILE)
    except FileNotFoundError:
        processed_df = pd.DataFrame(columns=df.columns)  # Initialize with same columns
    unique_column = "ResponseId"
    unprocessed_entries = df[~df[unique_column].isin(processed_df[unique_column]) & df["user_email"].notnull()]  # Replace "id" with your unique column
    # print(unprocessed_entries.columns)
    unprocessed_entries["EndDate"]=pd.to_datetime(unprocessed_entries["EndDate"])
    # print(len(unprocessed_entries))

    unprocessed_entries = (
    unprocessed_entries.sort_values(by=["user_uuid", "week", "EndDate"], ascending=[True, True, False])
    .drop_duplicates(subset=["user_uuid", "week"], keep="first")
    .sort_index()  # Optional: to restore the original row order
)   
    unprocessed_entries=unprocessed_entries.loc[unprocessed_entries[COLUMN_TO_PROCESS[1]]!="Invalid Score"]
    print(len(unprocessed_entries))
    print(unprocessed_entries[["user_email","week"]])
    # print(unprocessed_entries.columns)
    # Process new entries
    flag=False
    if not unprocessed_entries.empty:
        for _, row in unprocessed_entries.iterrows():
            to_email = row["user_email"]
            name=row["user_name"]
            score = row[COLUMN_TO_PROCESS[0]]
            classification = row[COLUMN_TO_PROCESS[1]]
            current_week=row["week"]

            


            if not (current_week is None or (isinstance(current_week, float) and math.isnan(current_week))):
                if is_email_sent(to_email, current_week):
                    print(f"Email already sent to {to_email} for week {current_week}. Skipping...")
                    flag=True
                    continue
                else:
                    print(to_email, current_week)
        # Call send_email function if `current_week` is valid
                    flag = send_email(to_email,name, score, classification, current_week)
                # flag=True
            else:
                print(f"Skipping email for {to_email} due to NaN value in current_week.")

        if flag:
            processed_df = pd.concat([processed_df, unprocessed_entries])
            processed_df.to_csv(PROCESSED_CSV_FILE, index=False)

            print("Processed new entries and updated the tracking file.")
    else:
        print("No new entries to process or valid data are missing.")

# Run the script


print(f"Current Date and Time: {current_datetime}")
create_visuals(True)
process_csv()
print("Process Done")