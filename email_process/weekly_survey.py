import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import urllib.parse
from utils import *
from credentials import *



survey_sent_tracking_csv="/home/sneupane/relief_study/data/csv_files/email_tracking.csv"

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
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["User ID"] == user_id and int(row["Week"]) == week:
                    return True
    except FileNotFoundError:
        # File does not exist, so no emails have been logged yet
        return False
    return False

# Function to send email
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


def send_email():
    try:
        receipient_name=""
        receipient_uuid=""
        # print(participant_hashmap)
        for id in participant_hashmap:
            # if id== "sameerthereds@gmail.com":                 
                receipient_name=participant_hashmap[id][1]
                receipient_uuid=participant_hashmap[id][0]
                
                recipient_email =id
                email_sent_date = datetime.now().date()
                current_week=user_days_week[id][0][email_sent_date]-1
                if is_email_sent(receipient_uuid, current_week):
                    print(f"Email already sent to {recipient_email} for week {current_week}. Skipping...")
                    continue


                custom_link = generate_qualtrics_link_weekly_survey(receipient_name, receipient_uuid, recipient_email,current_week)
                custom_link=shorten_url(custom_link)
                subject = "Weekly Survey Link"
                html_content = f"""

<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; background-color: #f4f4f9; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
            
            <!-- Header -->
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #007bff; font-size: 24px; margin: 0;">Your Weekly Survey has arrived!!!</h1>
                <p style="color: #555; font-size: 16px; margin: 10px 0 0;"></p>
            </div>
            
            <!-- Greeting -->
            <p style="font-size: 16px; color: #333;">Hi <strong>{receipient_name}</strong>,</p>
            
            <!-- Main Content -->
            <p style="font-size: 16px; color: #555;">
                Upon completion, you will receive a visual of your data to help you self-reflect on your experiences over the past week.
            </p>
            
            <!-- Call-to-Action Button -->
            <div style="text-align: center; margin: 30px 0;">
                <a href="{custom_link}" style="display: inline-block; padding: 15px 30px; font-size: 18px; color: white; background-color: #28a745; text-decoration: none; border-radius: 5px; font-weight: bold; box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);">
                    📝 Fill Out the Survey
                </a>
            </div>

            <!-- Earnings Section -->
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <p style="font-size: 16px; color: #333; font-weight: bold;">Your Earnings So Far: <span style="color: #28a745;">${cumulative_count[recipient_email]}</span></p>
                <p style="font-size: 14px; color: #555; margin: 5px 0 0;">
                    - By completing <strong>{weekly_survey_count[recipient_email]}</strong> weekly surveys so far: <strong>${weekly_survey_count[recipient_email]}</strong><br>
                    - By sharing <strong>{memories_count[recipient_email]}</strong> weekly memories so far: <strong>${memories_count[recipient_email]}</strong>
                </p>
            </div>

            <!-- Closing Note -->
            <p style="font-size: 16px; color: #555; text-align: center; margin-top: 20px;">
                Thank you for your time.
            </p>
            
            <!-- Signature Block -->
            <p>Warm regards,</p>
            <p><strong>The Relief Study Team</strong><br><strong>The mDOT Center</strong><br><strong>University of Memphis</strong></p>

            <!-- Footer -->
            <div style="text-align: center; margin-top: 30px; font-size: 12px; color: #888;">
                <hr style="margin: 20px 0;">
                <p>If you have any questions, feel free to reply to this email or reach out to us at:</p>
                <p><a href="mailto:reliefmdot@gmail.com" style="color: #007bff; text-decoration: none;">reliefmdot@gmail.com</a></p>
                <p style="margin-top: 10px;">You're receiving this email because you're a valued participant in our study.</p>
            </div>
        </div>
    </body>
</html>
                """

                # Create the email
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = EMAIL_ADDRESS
                msg["To"] = recipient_email

                # Attach the HTML content
                msg.attach(MIMEText(html_content, "html"))

                # Send the email using SMTP_SSL
                with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
                    server.login(EMAIL_ADDRESS, PASSWORD)  # Replace with your credentials
                    server.send_message(msg)
                    print(f"Email sent to {recipient_email} for week {current_week}")
                
                log_email_sent(receipient_uuid, receipient_name, current_week, email_sent_date)
    except Exception as e:
        print(f"Error: {e}")
current_datetime = datetime.now() 
print(f"Current Date and Time: {current_datetime}")
send_email()
   

print("Process Done")

