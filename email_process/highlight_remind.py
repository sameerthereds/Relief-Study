import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from credentials import *
from utils import *

# Constants
# Input file to check missing users
LOG_FILE = "/home/sneupane/relief_study/data/csv_files/highlights_reminder_log.csv"  # Log file to track sent emails

def send_reminder_email(to_email, user_name, today_date, current_week):
    subject = "Reminder: Please Share Your Latest CuesHub Memories"
    html_content = f"""
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; background-color: #f9f9f9; padding: 20px; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
            
            <!-- Header -->
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #007bff; font-size: 24px; margin: 0;">Share your Memories for Maximizing Study Compensation</h1>
                <p style="font-size: 16px; margin: 10px 0 0;"></p>
            </div>
            
            <!-- Main Content -->
            <p style="font-size: 16px; color: #333; text-align: left; margin: 20px 0;">
                Dear {user_name},
            </p>
            <p style="font-size: 16px; color: #555; text-align: left;">
                We noticed that we haven't received your CuesHub memories for this week. 
                Please share your weekly memories to maximize your study compensation.<br>
                
            </p>

            <!-- Additional Information -->
            <p style="font-size: 16px; color: #555; text-align: left;">
                Your weekly memories are truly essential for the study, helping us gain valuable insights! Thank you for your cooperation!
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
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email

        # Attach the HTML content
        msg.attach(MIMEText(html_content, "html"))

        # Send the email
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
            server.login(EMAIL_ADDRESS, PASSWORD)
            server.send_message(msg)
            print(f"Reminder email sent to {to_email}")
        
        # Log the email sent
        log_email_sent(user_name, to_email,today_date, current_week)
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")
        return False

def email_already_sent(user_name,user_email, today_date):
    """Check if an email has already been sent to the user today."""
    try:
        log_df = pd.read_csv(LOG_FILE)
        # Filter logs for the specific user and today's date
        sent_today = log_df[(log_df["user_name"] == user_name) & (log_df["user_email"] == user_email)&(log_df["date_sent"] == str(today_date))]
        return not sent_today.empty
    except FileNotFoundError:
        # If the log file doesn't exist, no emails have been sent
        return False
    except Exception as e:
        print(f"Error checking email log for {user_name}: {e}")
        return False

def log_email_sent(user_name,user_email, today_date, current_week):
    """Logs sent email into a CSV file."""
    log_entry = {
        "user_name": user_name,
        "user_email": user_email,
        "date_sent": today_date,
        "week": current_week
    }
    try:
        # Load existing log or create a new one
        try:
            log_df = pd.read_csv(LOG_FILE)
        except FileNotFoundError:
            log_df = pd.DataFrame(columns=["user_name", "user_email","date_sent", "week"])
        
        # Append new log entry
        log_df = pd.concat([log_df, pd.DataFrame([log_entry])], ignore_index=True)
        log_df.to_csv(LOG_FILE, index=False)
        print(f"Logged email sent to {user_name}")
    except Exception as e:
        print(f"Failed to log email for {user_name}. Error: {e}")

def check_missing_users(csv_path):
    """Check for users who haven't submitted and send reminders."""
    df = pd.read_csv(csv_path)
    for user in participant_hashmap:
        uuid = participant_hashmap[user][0]
        today = datetime.now().date()
        current_week = user_days_week[user][0][today] - 1
        
        # Filter user submissions for the current week
        user_df = df.loc[df["receipient_uuid"] == uuid]
        user_df = user_df[user_df['week'] == current_week]
        # print(user,current_week)
        if current_week > 0:
            if len(user_df) == 0:
                user_email = user
                user_name = participant_hashmap[user][1]
                if email_already_sent(user_name,user_name, today):
                    print(f"Email already sent to {user_name} today. Skipping.")
                    continue
                send_reminder_email(user_email, user_name, today, current_week)
            else:
                print(f"{user} has already submitted memories for week {current_week}.")

        else:
            print(f"{user} has not completed one week so far and still in week {current_week}.")

# Example usage
if __name__ == "__main__":
    current_datetime = datetime.now() 
    print(f"Current Date and Time: {current_datetime}")
    check_missing_users(Highlight_CSV_FILE)
    print("Process Done")