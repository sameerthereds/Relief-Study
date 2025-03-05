#!/usr/bin/env python

import imaplib
import email
from email.header import decode_header
import re
import csv
import os
import pickle
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from credentials import *
from utils import *
from datetime import datetime
# Configuration

# SEARCH_SUBJECT_MEMORIES = "CuesHub Memories"
SEARCH_SUBJECT_MEMORIES=[ "CuesHub Memories","My weekly memory from CuesHub"]
from datetime import datetime

import os
import csv
import imaplib
import email
from email.header import decode_header
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time

# Constants
# Check if an email has already been processed
def email_already_processed(url_id,receipient_uuid):
    """
    Check if an email (using its URL ID) has already been processed.
    """
    try:
        if not os.path.exists(Highlight_CSV_FILE):
            return False
        with open(Highlight_CSV_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get("email_id") == url_id and row.get("receipient_uuid")==receipient_uuid:
                    return True
        return False
    except Exception as e:
        print("Error: occured while checking email already processed or not")

# Save extracted data to CSV
def save_to_csv(email_id, sender, date, stressors):
    """
    Save the extracted data to a CSV file.
    """
    try:
        receipient_name=""
        receipient_uuid=""
        current_week=0
        parsed_date = datetime.strptime(date.strip("'"), "%a, %d %b %Y %H:%M:%S %z")
        print("J")
# Extract the date part
        date_only = parsed_date.date()  
        for id in participant_hashmap:
            if id in sender:
                receipient_name=participant_hashmap[id][1]
                receipient_uuid=participant_hashmap[id][0]
                current_week=user_days_week[id][0][date_only]-1
                print(current_week)
        
        file_exists = os.path.exists(Highlight_CSV_FILE)
        with open(Highlight_CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["email_id", "sender", "receipient_name","receipient_uuid","date", "stressors","week"])
            if not file_exists:
                print("I")
                writer.writeheader()
            writer.writerow({"email_id": email_id, "sender": sender,"receipient_name": receipient_name,"receipient_uuid": receipient_uuid, "date": date, "stressors": stressors,"week":current_week})
        print(f"Data saved: {email_id}, {sender}, {date},{receipient_name}, {receipient_uuid} ,{stressors},{current_week}")
    except Exception as e:
        print("Error: saving data in the csv file", e)

# Save the webpage as an HTML file
def save_webpage_as_html(url, folder_name, file_name):
    """
    Save the full HTML content of a webpage to a file inside a sender-specific folder.
    """
    # Create the sender-specific folder if it doesn't exist
    os.makedirs(folder_name, exist_ok=True)
    save_path = os.path.join(folder_name, file_name)

    # Set up Selenium
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print(f"Fetching webpage: {url}")
        driver.get(url)
        time.sleep(5)  # Wait for the page to load completely
        with open(save_path, "w", encoding="utf-8") as file:
            file.write(driver.page_source)
            print(f"Webpage saved as HTML at: {save_path}")
    except Exception as e:
        print(f"Error saving webpage as HTML: {e}")
    finally:
        driver.quit()

    return save_path

def extract_id_from_link(link):
    """
    Extract the unique ID from the URL query parameter 'id'.
    Example URL: https://www.cueshub.com/story?id=0731f95e-3c0c-411a-916a-cfa2e7abca47
    """
    # print("S")
    match = re.search(r"[?&]id=([a-fA-F0-9\-]+)", link)
    # print("S1")
    return match.group(1) if match else None

def extract_from_saved_html(html_file_path):
    """
    Extract stressors and their frequencies from a saved HTML file.
    Locate stressors after the note section and clean the extracted text.
    """
    try:
        # Open and parse the HTML file
        with open(html_file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        # # Locate the <p> tag containing the note
        all_paragraphs = soup.find_all("p")
        # print("Available <p> tags in the HTML:")
        note_section=[]
        for p in all_paragraphs:
            # print(p)
            text=(p.get_text(strip=True))
            if text[:4]=="Note":
                note_section.append(text)

        # note_section = soup.find(string=re.compile("Note: Your memory was generated from the following events you recorded:"))
        if  len(note_section) ==0 :
            print(f"Note section not found in HTML: {html_file_path}")
            return {"stressors": []}

        # Extract the full text from the note section
        stressors_text = " ".join(note_section)
        # Remove the leading "Note: Your memory was generated from the following events you recorded:"
        stressors_text = re.sub(r"Note:Your memory was generated from the following events you recorded:\s*", "", stressors_text)
        # print(stressors_text)
        # Remove the word "and" and split the text into stressors
        stressors_list = [
            item.strip() for item in re.split(r",|and", stressors_text) if item.strip()
        ]

        # Count the frequency of each stressor
        stressor_frequency = {}
        for stressor in stressors_list:
            # Extract frequency if present, e.g., "(2)"
            match = re.search(r"(.*?)\s*\((\d+)\)$", stressor)
            if match:
                stressor_name = match.group(1).strip()
                frequency = int(match.group(2))
            else:
                stressor_name = stressor
                frequency = 1

            # Update the frequency in the dictionary
            stressor_frequency[stressor_name] = stressor_frequency.get(stressor_name, 0) + frequency

        # Format as "stressor (frequency)"
        formatted_stressors = [
            f"{stressor} ({frequency})" for stressor, frequency in stressor_frequency.items()
        ]

        return {
            "stressors": formatted_stressors
        }

    except Exception as e:
        print(f"Error processing HTML file: {e}")
        return {"stressors": []}


def process_email( sender, date, link):
    """
    Process an email: use URL ID as the unique identifier, save webpage, extract data, and save results.
    """
    # Extract the unique ID from the URL
    # print(sender)
    try :
        # print("I4")
        # print(link)
        url_id = extract_id_from_link(link)
        # print(url_id)
        if not url_id:
            print(f"Unable to extract ID from link: {link}. Skipping email.")
            return
        
        # Check if this ID has already been processed
        # print(sender)
        # print(participant_hashmap)
        receipient_name,receipient_uuid="",""
        for id in participant_hashmap:
            if id in sender:
                receipient_name=participant_hashmap[id][1]
                receipient_uuid=participant_hashmap[id][0]
        # print("I3")

        if email_already_processed(url_id,receipient_uuid):
            print(f"Email with URL ID {url_id}  from user {receipient_name} : {receipient_uuid} has already been processed. Skipping.")
            return

        # Create folder name based on sender
        # print("I1")
        folder_name = os.path.join(html_save_path, sender.replace("@", "_").replace(".", "_"))
        # print("I2")
        # Generate filename based on email date
        file_name = f"{date.replace(':', '-').replace(' ', '_')}.html"

        # Save the webpage as HTML
        
        html_path = save_webpage_as_html(link, folder_name, file_name)
        
        # Extract information from the saved HTML file
        extracted_data = extract_from_saved_html(html_path)
        # print(extracted_data)
        # print(type(extracted_data))
        # bold_words = ", ".join([f"{word} ({freq})" for word, freq in extracted_data["stressors"]])
        bold_words=" , ".join(extracted_data["stressors"])
        # print(bold_words)
        # Save extracted data to CSV
        # print(sender)
        save_to_csv(url_id, sender, date, bold_words)
    except Exception as e:
        print("Error: processing the email before saving in csv file")

# Extract link from the email body
def extract_link(email_body):
    """
    Extract the first link from the email body.
    """
    try:
        link_match = re.search(r"http[s]?://\S+", email_body)
        return link_match.group(0) if link_match else None
    except Exception as e:
        return None
        print("Error: cannot extract the link from the email body")

# Fetch emails from Gmail
def fetch_emails():
    """
    Connect to Gmail, fetch emails with the subject "CuesHub Memories", and process them.
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, PASSWORD)
        mail.select("inbox")
        for search_text in SEARCH_SUBJECT_MEMORIES:
        # Search for emails with the specified subject
            status, messages = mail.search(None, f'SUBJECT "{search_text}"')
            email_ids = messages[0].split()
            print(len(email_ids))
            for email_id in email_ids:
                # Fetch the email
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = decode_header(msg["Subject"])[0][0]
                        sender = msg["From"].lower()
                        # print(sender)
                        date = msg["Date"]

                        if isinstance(subject, bytes):
                            subject = subject.decode()

                        # Convert email date into ISO format
                        email_datetime = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
                        email_id_iso = email_datetime.isoformat()
                        # print(email_datetime,email_id_iso)
                        # Extract the email body
                        email_body = None
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                if content_type in ["text/plain", "text/html"]:
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        email_body = payload.decode(errors="ignore")
                                        break
                        else:
                            payload = msg.get_payload(decode=True)
                            if payload:
                                email_body = payload.decode(errors="ignore")

                        if not email_body:
                            print(f"Unable to extract email body for email ID {email_id_iso}.")
                            continue

                        # Extract the link from the email body
                        link = extract_link(email_body)
                        if not link:
                            print(f"No link found in email ID {email_id_iso}.")
                            continue
                        # Process the email
                        process_email( sender, date, link)

    except Exception as e:
        print(f"Error fetching emails: {e}")

# Main
if __name__ == "__main__":
    current_datetime = datetime.now()    
    print(f"Current Date and Time: {current_datetime}")
    result = backup_csv_file(Highlight_CSV_FILE)
    print(result)
    fetch_emails()