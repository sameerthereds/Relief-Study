import pandas as pd
from datetime import datetime
import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from credentials import *
from utils import *
import warnings
warnings.filterwarnings("ignore")
# Constants
# Input file to check missing users
LOG_FILE = "/home/sneupane/relief_study/data/csv_files/share_stressors_reminder_log.csv"  # Log file to track sent emails







def send_reminder_email(to_email, user_name, today_date):
    """Send a reminder email to the user."""
    subject = "Reminder: Please Share Your Stressors"
    html_content = f"""
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; background-color: #f9f9f9; padding: 20px; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
            
            <!-- Header -->
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #007bff; font-size: 24px; margin: 0;">DO NOT MISS OUT ON CUTTING EDGE STRESS INTERVENTIONS</h1>
                <p style="font-size: 16px; margin: 10px 0 0;"></p>
            </div>
            
            <!-- Main Content -->
            <p style="font-size: 16px; color: #333; text-align: left; margin: 20px 0;">
                Dear {user_name},
            </p>
            <p style="font-size: 16px; color: #555; text-align: left;">
               Please share your events via CuesHub app to receive innovative stress interventions tailored to your stress management needs.
            </p>

            <!-- Additional Information -->
            <p style="font-size: 16px; color: #555; text-align: left;">
                Thank you for your continued support!
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
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, PASSWORD)
            server.send_message(msg)
            print(f"Reminder email sent to {to_email}")
        
        # Log the email sent
        log_email_sent(user_name, today_date.date())
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")
        return False

def email_already_sent(user_name, today_date):
    """Check if an email has already been sent to the user today."""
    try:
        log_df = pd.read_csv(LOG_FILE)
        # Filter logs for the specific user and today's date
        sent_today = log_df[(log_df["user_name"] == user_name) & (log_df["date_sent"] == str(today_date.date()))]
        return not sent_today.empty
    except FileNotFoundError:
        # If the log file doesn't exist, no emails have been sent
        return False
    except Exception as e:
        print(f"Error checking email log for {user_name}: {e}")
        return False

def log_email_sent(user_name, today_date):
    """Log sent email details into a CSV file."""
    log_entry = {
        "user_name": user_name,
        "date_sent": today_date
    }
    try:
        # Load existing log or create a new one
        try:
            log_df = pd.read_csv(LOG_FILE)
        except FileNotFoundError:
            log_df = pd.DataFrame(columns=["user_name", "date_sent"])

        # Append new log entry
        log_df = pd.concat([log_df, pd.DataFrame([log_entry])], ignore_index=True)
        log_df.to_csv(LOG_FILE, index=False)
        print(f"Logged email for {user_name}")
    except Exception as e:
        print(f"Failed to log email for {user_name}. Error: {e}")

def check_users_and_send_reminders(csv_path):
    """Check the SQLite database for user entries and send reminders if no entries in the last 3 days."""
    try:
        # Connect to the database
        df = pd.read_csv(csv_path)

        # Get the current date and calculate the cutoff date (3 days ago)
        today = datetime.now()
        cutoff_date = today - timedelta(days=3)
        cutoff_date=cutoff_date.date()
        # print(cutoff_date)
        # Query the database for distinct users
       

        for user in participant_hashmap:
            
            sender_name=participant_hashmap[user][1]

            user_df = df[df['sender_name'] == sender_name]

            # Convert dates to proper format and filter
            user_df['date'] = pd.to_datetime(user_df['date']).dt.date
            recent_entries = user_df[user_df['date'] >= cutoff_date]
            # print(recent_entries[["date","stressor"]])
            # print(user,len(recent_entries))            
            if recent_entries.empty:
                # Check if an email has already been sent today
                if email_already_sent(sender_name, today):
                    # print(user, "I")
                    print(f"Email already sent to {sender_name} today. Skipping.")
                else:
                    # Send a reminder email
                    # pass
                    send_reminder_email(user, sender_name, today)
            else:
                print(f"{user} has entries within the last 3 days.")

    

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    current_datetime = datetime.now()

    print(f"Current Date and Time: {current_datetime}")
    check_users_and_send_reminders(extracted_csv_path)