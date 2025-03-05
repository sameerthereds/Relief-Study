import os
import re
import pickle
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from credentials import *

# --- Configuration ---
# Email settings: update with your actual credentials and SMTP server details.


# Log file extensions to consider
LOG_EXTENSIONS = ('.log', '.txt')

# File to store last checked positions
LOG_TRACKING_FILE = "/home/sneupane/relief_study/data/logs/log_tracking.pkl"
FROM_EMAIL="reliefmdot@gmail.com"
TO_EMAIL="sameerthereds@gmail.com"

# --- Email Sending Function ---
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(FROM_EMAIL, PASSWORD)
            server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Error sending email: {e}")


# --- Function to get log files from directories ---
def get_log_files(directories):
    """
    Recursively walk through each provided directory and collect files that match log extensions.
    """
    log_files = []
    for directory in directories:
        if not os.path.exists(directory):
            print(f"Directory does not exist: {directory}")
            continue
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(LOG_EXTENSIONS):
                    log_files.append(os.path.join(root, file))
    return log_files


# --- Function to load last checked positions ---
def load_last_checked_positions():
    if os.path.exists(LOG_TRACKING_FILE):
        with open(LOG_TRACKING_FILE, 'rb') as f:
            return pickle.load(f)
    return {}


# --- Function to save last checked positions ---
def save_last_checked_positions(positions):
    with open(LOG_TRACKING_FILE, 'wb') as f:
        pickle.dump(positions, f)


# --- Function to check log files for errors and collect them ---
def check_logs_in_files(log_files, last_positions):
    """
    For each log file, resume from the last checked position and scan for errors.
    Instead of sending an email for each error, all detected errors are collected
    and returned as a list of error messages.
    """
    errors_found = []
    # Regex pattern to detect "error" or "errno" (case-insensitive)
    error_pattern = re.compile(r'error|errno', re.IGNORECASE)

    for log_file in log_files:
        if not os.path.exists(log_file):
            print(f"File not found: {log_file}")
            continue

        last_pos = last_positions.get(log_file, 0)
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                f.seek(last_pos)
                file_errors = []
                for line in f:
                    if error_pattern.search(line):
                        file_errors.append(line.strip())
                # Update the last checked position for this file
                last_positions[log_file] = f.tell()
                
                if file_errors:
                    error_message = f"Errors in {log_file}:\n" + "\n".join(file_errors)
                    errors_found.append(error_message)
        except Exception as e:
            # Log file access errors (including Errno errors)
            error_message = f"Error processing {log_file}: {e}"
            errors_found.append(error_message)

    return errors_found


# --- Main execution ---
if __name__ == "__main__":
    # List directories to check (absolute or relative paths)
    directories_to_check = [
        "/home/sneupane/relief_study/data/logs/email_process",
         "/home/sneupane/relief_study/data/logs/engagement",
          "/home/sneupane/relief_study/data/logs/highlight",
          "/home/sneupane/relief_study/data/logs/participant",
           "/home/sneupane/relief_study/data/logs/qualtrics",
            "/home/sneupane/relief_study/data/logs/visualization",
             "/home/sneupane/relief_study/data/logs/weekly_survey",
        
        # Add additional directories as needed
    ]

    # Load last checked positions
    last_checked_positions = load_last_checked_positions()

    # Get the list of log files from the directories
    log_files = get_log_files(directories_to_check)
    if not log_files:
        print("No log files found.")
    else:
        print("Log files found:")
        for f in log_files:
            print(f" - {f}")

        # Check log files for errors and collect error messages
        all_errors = check_logs_in_files(log_files, last_checked_positions)

        # If errors were found, send one email with all the details
        if all_errors:
            subject = "Aggregated Error Report from Log Files"
            body = "\n\n".join(all_errors)
            send_email(subject, body)
            print("Aggregated error email sent.")
        else:
            print("No new errors detected.")

        # Save updated last checked positions
        save_last_checked_positions(last_checked_positions)



