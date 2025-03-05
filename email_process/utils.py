import os
import imaplib
import smtplib
from email.message import EmailMessage
import email
import re
from datetime import datetime
from bs4 import BeautifulSoup
import sqlite3
import shutil
import time
from PIL import Image
import pytesseract
import datetime as datetime_adj
from datetime import datetime
import re
import numpy as np
import csv
import pandas as pd
import cv2
from urllib.parse import urlencode
import requests
import pickle

FOUND_EMAILS_DB = '/home/sneupane/relief_study/data/databases/found_emails.db'
FOUND_EMAILS_CSV='/home/sneupane/relief_study/data/databases/found_emails.csv'
EXTRACTED_WORDS_INTERVENTION_DB = '/home/sneupane/relief_study/data/databases/extracted_words_interventions.db'
EXTRACTED_WORDS_ALL_DB = '/home/sneupane/relief_study/data/databases/extracted_words_all.db'
ATTACHMENTS_FOLDER = '/home/sneupane/relief_study/data/saved_files/attachments'

positive_template_path = '/home/sneupane/relief_study/email_process/templates_for_valence/positive.jpg'
neutral_template_path = '/home/sneupane/relief_study/email_process/templates_for_valence/neutral.jpg'
negative_template_path = '/home/sneupane/relief_study/email_process/templates_for_valence/negative.jpg'

Highlight_CSV_FILE = "/home/sneupane/relief_study/data/csv_files/stressors.csv"
html_save_path="/home/sneupane/relief_study/data/saved_files/saved_html"
# backups_main_folder = "/data/sneupane/relief_study/data/databases/backups"
backups_main_folder = "/home/sneupane/relief_study/data/databases/backups"
extracted_csv_path="/home/sneupane/relief_study/data/csv_files/extracted_stressor_location.csv"
all_extracted_csv_path="/home/sneupane/relief_study/data/csv_files/all_extracted_stressor_location.csv"








with open("/home/sneupane/relief_study/data/Participants_Pool/active_users.pickle", "rb") as file:
        participant_hashmap = pickle.load(file)
# print(participant_hashmap)

# print(participant_hashmap)

with open("/home/sneupane/relief_study/data/Participants_Pool/memories_count.pickle", "rb") as file:
        memories_count = pickle.load(file)

with open("/home/sneupane/relief_study/data/Participants_Pool/cumulative_count.pickle", "rb") as file:
        cumulative_count = pickle.load(file)

with open("/home/sneupane/relief_study/data/Participants_Pool/weekly_survey_count.pickle", "rb") as file:
        weekly_survey_count = pickle.load(file)

with open("/home/sneupane/relief_study/data/Participants_Pool/user_days_week.pickle", "rb") as file:
        user_days_week = pickle.load(file)

ROI_TOP_LEFT = (76, 436)  # (x, y)
ROI_BOTTOM_RIGHT = (640, 578)  # (x, y)
templates = {
    "Positive": positive_template_path,
    "Neutral": neutral_template_path,
    "Negative": negative_template_path
}

def backup_databases(database_paths):
    """
    Create a folder named 'backups' if it doesn't exist.
    Inside that folder, create a timestamped folder 
    'databases_backup_<YYYY-MM-DD_HH-MM-SS>' and copy 
    specified database files into it.
    
    :param database_paths: A list of file paths to databases you want to back up.
    """
    # 1. Create or confirm the top-level 'backups' folder
    try:
        os.makedirs(backups_main_folder, exist_ok=True)
        
        # 2. Create a timestamp for the subfolder name
        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_subfolder_name = f"databases_backup_{current_time}"
        
        # 3. Create the subfolder path inside 'backups'
        backup_subfolder_path = os.path.join(backups_main_folder, backup_subfolder_name)
        os.makedirs(backup_subfolder_path, exist_ok=True)

        # 4. Copy each database file into the backup subfolder
        for db_path in database_paths:
            if os.path.isfile(db_path):
                db_filename = os.path.basename(db_path)  # Extract filename
                destination = os.path.join(backup_subfolder_path, db_filename)
                try:
                    shutil.copy2(db_path, destination)
                    print(f"Backed up '{db_filename}' to '{backup_subfolder_path}'")
                except Exception as e:
                    print(f"Error copying '{db_path}': {e}")
            else:
                print(f"File not found or invalid: {db_path}")
    except Exception as e:
        print("Error: in creating backup databases", e)

def backup_csv_file(file_path, backup_folder="/home/sneupane/relief_study/data/csv_files/backups"):
    """
    Copies a given CSV file to the specified backup folder with the current datetime appended to the filename.

    Args:
        file_path (str): Path to the CSV file to be backed up.
        backup_folder (str): Folder where the backup will be stored. Defaults to 'backups'.

    Returns:
        str: Message indicating success or error.
    """
    try:
        # Check if the file exists
        if not os.path.isfile(file_path):
            return f"Error: The file '{file_path}' does not exist."
        
        # Create the backup folder if it doesn't exist
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        
        # Extract the original file name and extension
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        
        # Get the current datetime and format it
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Construct the new file name with datetime
        new_file_name = f"{file_name}_{current_datetime}{file_extension}"
        
        # Construct the full destination path
        destination_path = os.path.join(backup_folder, new_file_name)
        
        # Copy the file to the destination
        shutil.copy(file_path, destination_path)
        
        return f"File '{file_path}' successfully backed up to '{destination_path}'."
    except Exception as e:
        return f"An error occurred: {e}"
    

def setup_databases():
    """Create tables in the databases if they do not exist."""
    # Found Emails Database
    # print(FOUND_EMAILS_DB)
    try:
        with sqlite3.connect(FOUND_EMAILS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS found_emails (
                            email_id TEXT PRIMARY KEY,
                                email_datetime TEXT,
                            sender TEXT,
                            sender_name TEXT,
                            sender_uuid TEXT,
                           stressor TEXT,
                           stressor_date TEXT,
                           email_processed_date TEXT)''')
            conn.commit()

        # Extracted Words Database
        with sqlite3.connect(EXTRACTED_WORDS_INTERVENTION_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS extracted_words (
                            email_id TEXT PRIMARY KEY,
                            sender TEXT,
                            sender_name TEXT,
                            sender_uuid TEXT,
                            date TEXT,
                            stress_date TEXT,
                            valence TEXT,
                            stressor TEXT,
                            location TEXT,              
                        intervention_type TEXT,
                            intervention TEXT,
                           email_processed_date TEXT,
                           prompt TEXT)''')
            conn.commit()

        with sqlite3.connect(EXTRACTED_WORDS_ALL_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS extracted_words (
                            email_id TEXT PRIMARY KEY,
                            sender TEXT,
                            sender_name TEXT,
                            sender_uuid TEXT,
                            date TEXT,
                            stress_date TEXT,
                            valence TEXT,
                            stressor TEXT,
                            location TEXT,              
                        intervention_type TEXT,
                            intervention TEXT,
                           email_processed_date TEXT,
                           prompt TEXT)''')
            conn.commit()
    except Exception as e:
        print("Error: in setting up databases", e)



# def email_already_processed(email_id):
#     """Check if an email with the given ID has already been processed."""
#     try:
#         with sqlite3.connect(FOUND_EMAILS_DB) as conn:
#             cursor = conn.cursor()
#             # query = """
#             #     SELECT email_id FROM found_emails
#             #     WHERE email_id = ? OR (sender_uuid = ? AND date = ?)
#             # """
#             cursor.execute("SELECT email_id FROM found_emails WHERE email_id = ?", (email_id,))
#             # cursor.execute(query, (email_id, sender_uuid, stressor_date))
#             return cursor.fetchone() is not None
        
#     except Exception as e:
#         print("Error: in checking email already processed", e)
#         return False

def email_already_processed(email_id, check_in_csv=False):
    """Check if an email with the given ID has already been processed in either a CSV file or a database."""
    try:
        if check_in_csv:
            # Check in CSV file
            try:
                df = pd.read_csv(FOUND_EMAILS_CSV)
                return email_id in df['email_id'].values
            except Exception as e:
                print("Error reading CSV file:", e)
                return False
        else:
            # Check in SQLite database
            with sqlite3.connect(FOUND_EMAILS_DB) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT email_id FROM found_emails WHERE email_id = ?", (email_id,))
                return cursor.fetchone() is not None

    except Exception as e:
        print("Error in checking email already processed:", e)
        return False
    
def stressor_already_processed(sender_uuid, stressor, stressor_date):
    """Check if an email with the given ID has already been processed."""
    try:
        with sqlite3.connect(FOUND_EMAILS_DB) as conn:
            cursor = conn.cursor()
            query = """
                SELECT email_id FROM found_emails
                WHERE sender_uuid = ? AND stressor = ? AND stressor_date = ?
            """
     
            cursor.execute(query, ( sender_uuid, stressor, stressor_date))
            return cursor.fetchone() is not None
        
    except Exception as e:
        print("Error: in checking stressor already processed", e)
        return False

def save_email_id(email_id,email_datetime,sender,sender_name,sender_uuid,stressor,stressor_date,email_processed_date):
    """Save the email ID in the found emails database."""
    try:
        with sqlite3.connect(FOUND_EMAILS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO found_emails (email_id,email_datetime,sender,sender_name,sender_uuid,stressor,stressor_date,email_processed_date) VALUES (?,?,?,?,?,?,?,?)", (email_id,email_datetime,sender,sender_name,sender_uuid,stressor,stressor_date,email_processed_date))
            conn.commit()
    except Exception as e:
        print("Error: in saving email id", e)

def save_extracted_words_intervention(email_id, sender,sender_name,sender_uuid, date, bold_words,intervention_type,intervention,email_processed_date,prompt):
    """Save extracted words, sender, and date in the extracted words database."""
    try:
        with sqlite3.connect(EXTRACTED_WORDS_INTERVENTION_DB) as conn:
            cursor = conn.cursor()
            # cursor.execute("INSERT INTO extracted_words (email_id, sender, date, bold_words) VALUES (?, ?, ?, ?)",
            #                (email_id, sender, date, '\n'.join(bold_words)))
            cursor.execute("INSERT INTO extracted_words (email_id, sender,sender_name,sender_uuid, date, stress_date,valence,stressor,location,intervention_type,intervention,email_processed_date,prompt) VALUES (?, ?, ?,?,?,?, ?,?,?,?,?,?,?)",
                        (email_id, sender, sender_name,sender_uuid,date, bold_words["date"],bold_words["valence"], bold_words["Stressor"], bold_words["Location"],intervention_type,intervention,email_processed_date,prompt))
            conn.commit()
    except Exception as e:
        print("Error: in saving extracted words interventions", e)


def save_extracted_words_all(email_id, sender,sender_name,sender_uuid, date, bold_words,intervention_type,intervention,email_processed_date,prompt):
    """Save extracted words, sender, and date in the extracted words database."""
    try:
        with sqlite3.connect(EXTRACTED_WORDS_ALL_DB) as conn:
            cursor = conn.cursor()
            # cursor.execute("INSERT INTO extracted_words (email_id, sender, date, bold_words) VALUES (?, ?, ?, ?)",
            #                (email_id, sender, date, '\n'.join(bold_words)))
            cursor.execute("INSERT INTO extracted_words (email_id, sender,sender_name,sender_uuid, date, stress_date,valence,stressor,location,intervention_type,intervention,email_processed_date,prompt) VALUES (?, ?, ?,?,?,?, ?,?,?,?,?,?,?)",
                        (email_id, sender, sender_name,sender_uuid,date, bold_words["date"],bold_words["valence"], bold_words["Stressor"], bold_words["Location"],intervention_type,intervention,email_processed_date,prompt))
            conn.commit()
    except Exception as e:
        print("Error: in saving extracted words all", e)

ROI_TOP_LEFT_RATIO = (0.1, 0.2)  # Fraction of width and height (e.g., 10% from left, 50% from top)
ROI_BOTTOM_RIGHT_RATIO = (0.99, 0.45)  # Fraction of width and height (e.g., 80% from left, 80% from top)
def resize_image_to_template(input_image, templates):
    """
    Resizes the input image to match the dimensions of the templates.
    """
    try:
    # for option, template_path in templates.items():
            # Load the template
        template = cv2.imread(positive_template_path, cv2.IMREAD_GRAYSCALE)
        

        # Get the dimensions of the template
        template_height, template_width = template.shape[:2]

        # Resize the input image to the template's dimensions
        resized_image = cv2.resize(input_image, (template_width, template_height))
        

        return resized_image
    except Exception as e:
        print("Error: in resizing image", e)
        return None


def detect_selected_option(input_image_path, templates):
    # Load the input image

    try:
        input_image = cv2.imread(input_image_path)
        input_image=resize_image_to_template(input_image,templates)

        if input_image is None:
            print("Failed to load the input image.")
            return None

        # Calculate the absolute coordinates of the ROI based on image dimensions
        height, width, _ = input_image.shape
        x1 = int(ROI_TOP_LEFT_RATIO[0] * width)
        y1 = int(ROI_TOP_LEFT_RATIO[1] * height)
        x2 = int(ROI_BOTTOM_RIGHT_RATIO[0] * width)
        y2 = int(ROI_BOTTOM_RIGHT_RATIO[1] * height)

        # Crop the ROI
        roi = input_image[y1:y2, x1:x2]
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Visualize the cropped ROI
        # plt.figure(figsize=(10, 5))
        # plt.subplot(1, 2, 1)
        # plt.imshow(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
        # plt.title("Cropped ROI")
        # plt.axis("off")

        # plt.subplot(1, 2, 2)
        # plt.imshow(gray_roi, cmap="gray")
        # plt.title("Grayscale ROI")
        # plt.axis("off")
        # plt.show()

        max_match = 0
        selected_option = None

        # Iterate through the templates
        for option, template_path in templates.items():
            # Load the template
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

            if template is None:
                print(f"Failed to load template for {option}.")
                continue

            # Perform template matching on the ROI
            result = cv2.matchTemplate(gray_roi, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            # print(f"Matching confidence for {option}: {max_val}")

            # Check if this match is the best so far
            if max_val > max_match:
                max_match = max_val
                selected_option = option

        # Return the selected option if the match is above a threshold
        if max_match > 0.7:  # Adjust threshold as needed
            return selected_option
        else:
            return "Not Detected"
    except Exception as e:
        print("Error: in extracting valence", e)
        return None



def extract_text_from_image(image_path):
    # print(image_path)
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)   
    return text





def extract_fields(extracted_text):
    try:
        date_match = re.search(r"[A-Za-z]{3}, [A-Za-z]{3} \d{1,2}", extracted_text)  # Match 'Tue, Nov 26'
        date = date_match.group(0) if date_match else "Date not found"
        
        time_match = re.search(r"\d{1,2}:\d{2} (AM|PM)", extracted_text)  # Match '01:44 PM'
        time = time_match.group(0) if time_match else "Time not found"
        
        # Extract "What was going on?"
        event_match = re.search(r"What was going on\?\s*(.+)", extracted_text)
        event = event_match.group(1).strip() if event_match else "Event not found"
        event=event.rstrip(" x")
        # Extract "Where was this located?"
        location_match = re.search(r"Where was this located\?\s*(.+)", extracted_text)
        location = location_match.group(1).strip() if location_match else "Location not found"
        location=location.rstrip(" x")
        if "Delete" in location:
            location = "Location not found"

        extracted_info = {
            "date": date + " at " + time,
            "Stressor": event,
            "Location": location,
        
        }
        return extracted_info
    except Exception as e:
        print("Error: in extracting info from CuesHub email", e)
        return None




def save_images_from_email(sender_folder, email_message, email_from, email_date):
    """Extract and save images from email attachments, naming them after the sender and date/time."""
    try:
        info={}
        image_found=False
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            # print(part)
            # Check if this part is an image
            if "attachment" in content_disposition or content_type.startswith("image/"):
                try:
                    image_found=True
                 
                    # Format the date and time for the filename
                    date_str = datetime.strptime(email_date, '%a, %d %b %Y %H:%M:%S %z').strftime('%Y%m%d_%H%M%S')
                    sanitized_sender = re.sub(r'[<>:"/\\|?*]', '_', email_from)  # Remove invalid filename characters
                    sanitized_sender=sanitized_sender.lower()
                    # Create a unique filename for each image with the sender's email and date-time
                    filename = f"{sanitized_sender}_{date_str}.jpg"  # Default to .jpg extension for simplicity
                    file_path = os.path.join(sender_folder, filename)
                    # print(file_path)
                    
                    # Save the image file
                    with open(file_path, "wb") as f:
                        f.write(part.get_payload(decode=True))


                    extracted_text = extract_text_from_image(file_path)
                    # print(extracted_text)
                    info = extract_fields(extracted_text)
                    selected_option = detect_selected_option(file_path, templates)
                    info["valence"]=selected_option
                    # print(f"Selected option: {selected_option}")
                    print(info)
                    print(f"Image saved successfully at {file_path}")
                    return info
                except Exception as e:
                    print(f"Failed to save image: {e}")
                    return "None"
        
        if image_found==False:
            print("No attachments found")
            return info    
    except Exception as e:
        print(f"Failed to save image or image not found: {e}")
        return "None" 
            



def time_to_time_of_day(i):
    
    try:
        tmp=""
        if  datetime_adj.time(5, 0)<=i.time() < datetime_adj.time(12, 0):
            tmp="Morning"
        elif  datetime_adj.time(12, 0,0)<=i.time() < datetime_adj.time(17, 0,0):
            tmp= "Afternoon"
        elif  datetime_adj.time(17, 0,0)<=i.time() < datetime_adj.time(21, 0,0):
            tmp= "Evening"
        elif  datetime_adj.time(21, 0,0)<=i.time() <= datetime_adj.time(23, 59,59):
            tmp= "Night"
        elif  datetime_adj.time(0, 0,0)<=i.time() < datetime_adj.time(5, 0,0):
            tmp= "Night"
            
        if tmp == "":
            print(str(i) + " :" +str(i.time()))
        return tmp
    except Exception as e:
        print("Error: in converting time to time of day", e)
        return None


def return_datetime(text):

    try:

    # Convert the string to a datetime object
        day_map = {
        "Mon": "Monday",
        "Tue": "Tuesday",
        "Wed": "Wednesday",
        "Thu": "Thursday",
        "Fri": "Friday",
        "Sat": "Saturday",
        "Sun": "Sunday"
        }

    # Extract abbreviated day and time of day
        day_abbr = text.split(',')[0]  # Extract day abbreviation (e.g., "Thu")
        time_of_day = text.split("at")[-1].strip()  # Extract time part (e.g., "02:38 PM")

        # Look up the full weekday name
        day_of_week = day_map.get(day_abbr, "Unknown day")

        # Parse the time part into a datetime object
        parsed_time = datetime.strptime(time_of_day, "%I:%M %p")
        return day_of_week, time_to_time_of_day(parsed_time)
        # Print results
        # print("Day of the week:", day_of_week)
        # print("Time of day:", time_of_day, time_to_time_of_day(time_of_day))
    except Exception as e:
        print("Error: in datetime code", e)
        return None,None
    





# Base Qualtrics survey URL
BASE_FORM_URL_INTERVENTION = "https://memphis.co1.qualtrics.com/jfe/form/SV_0210QW07yWSFca2"

def generate_qualtrics_link_intervention(user_id, receipient_uuid,stressor, location, date, intervention,intervention_type):
    """
    Generate a pre-filled Qualtrics survey link with URL-encoded parameters.
    """
    # Create a dictionary of query parameters
    try:
        query_params = {
            "user_id": user_id,
            "stressor": stressor,
            "location": location,
            "date": date,
            "intervention": intervention,
            "intervention_type":intervention_type,
             "uuid":receipient_uuid
        }

        # Encode the query parameters
        encoded_params = urlencode(query_params)

        # Append the encoded parameters to the base URL
        full_url = f"{BASE_FORM_URL_INTERVENTION}?{encoded_params}"
        return full_url
    except Exception as e:
        print("Error: in creating qualtrics link", e)
        return None
    

BASE_FORM_URL_WEEKLY_SURVEY = "https://memphis.co1.qualtrics.com/jfe/form/SV_4U6Q2jXuHGXNTkq"

def generate_qualtrics_link_weekly_survey(user_id, receipient_uuid,receipeint_email,current_week):
    """
    Generate a pre-filled Qualtrics survey link with URL-encoded parameters.
    """
    # Create a dictionary of query parameters
    try:
        query_params = {
            "user_name": user_id,
            "user_uuid":receipient_uuid,
            "user_email":receipeint_email,
            "week":current_week
        }
        
        # Encode the query parameters
        encoded_params = urlencode(query_params)

        # Append the encoded parameters to the base URL
        full_url = f"{BASE_FORM_URL_WEEKLY_SURVEY}?{encoded_params}"
        return full_url
    except Exception as e:
        print("Error: in creating qualtrics link", e)
        return None

def shorten_url(long_url):
    """
    Shorten a URL using the TinyURL API.
    """
    try:
        # TinyURL API endpoint
        api_url = "https://tinyurl.com/api-create.php"
        
        # Make a GET request to TinyURL
        response = requests.get(api_url, params={"url": long_url})
        response.raise_for_status()
        
        # Return the shortened URL
        return response.text
    except Exception as e:
        print(f"Error shortening URL: {e}")
        return long_url  # Fallback to the original URL

