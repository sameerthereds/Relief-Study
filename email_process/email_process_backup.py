from credentials import get_responses
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils import *
from credentials import *
import pandas as pd
from datetime import timezone, timedelta

# from email_name_hashmap import hashmap
# print(credentials.client)
import pickle,random
from datetime import datetime

SEARCH_SUBJECT =['My CuesHub Event','CuesHub prompted me for']
# SEARCH_SUBJECT="CuesHub prompted me for"

# with open('/home/sneupane/LLM_experiments/intervention_steps_dict.pickle', 'rb') as handle:
#     intervention_steps_dict = pickle.load(handle)

with open('/home/sneupane/LLM_experiments/refined_interventions.pickle', 'rb') as handle:
    intervention_steps_dict = pickle.load(handle)


# generic_prompts = [
#     "You are a stress intervention specialist. A user feels so overwhelmed right now and doesn’t know what to do. Can you help them manage this stress?",
#     "A user is feeling really anxious and tense. Can you suggest something to help them calm down?",
#     "A user is dealing with too much stress and is struggling to handle it. What’s a simple way to help them feel better?",
#     "A user feels like they’re carrying a heavy burden of stress. Can you offer a practical way to ease their tension?",
#     "A user is frustrated and stressed out. They need something to help them relax right now. Can you assist?",
#     "A user is overwhelmed and doesn’t know how to cope with everything. What can they do to manage their stress?",
#     "A user is constantly feeling stressed, and it’s starting to affect them deeply. Can you recommend a good intervention?",
#     "A user is so stressed out that they’re struggling to stay focused. Can you suggest something to help them calm down quickly?",
#     "A user feels like they’re losing control because of stress. What’s a good way to help them ground themselves and feel better?",
#     "A user feels like they’re at their breaking point from all the stress. Can you help them find relief right now?"
# ]

def database_csv(database_path,csv_file_name):
    # database_path = "/home/sneupane/relief_study/email_process/databases/extracted_words.db"

# Establish a connection to the SQLite database
    connection = sqlite3.connect(database_path)

    # List all tables in the database
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql(query, connection)


    # Load data from a specific table into a Pandas DataFrame
    table_name = "extracted_words"  # Replace with the table name you want to extract
    extracted_words_df = pd.read_sql(f"SELECT * FROM {table_name}", connection)
    extracted_words_df['date'] = pd.to_datetime(extracted_words_df['date'], errors='coerce')
    target_offset = timezone(timedelta(hours=-6))

# Convert all timestamps to the target timezone
    extracted_words_df['date'] = extracted_words_df['date'].apply(lambda dt: dt.astimezone(target_offset))
    extracted_words_df['date'] = extracted_words_df['date'].dt.strftime('%a, %d %b %Y %H:%M:%S %z')

    connection.close()

    extracted_words_df.to_csv(csv_file_name, index=False)

def create_prompt(c):
    # print(c)
    datetime=c["date"]
    stressor=c["Stressor"]
    location=c["Location"]
    # day, time=return_datetime(datetime)
    intervention_type,interventions="",""
    # print(day_of_week,time_of_day)

    if stressor!="Event not found" and location!="Location not found":
        day_of_week, time_of_day = return_datetime(datetime)
        intervention_type = random.choice(['Targeted', 'Generic'])
    else:
        intervention_type = 'Generic'
    
    # intervention_type = 'Generic'
    
    if intervention_type == 'Targeted':
       
        curr_prompt=f""" 
        You are a stress intervention specialist. Based on the given {stressor} and {location}, provide detailed steps for the single best intervention to manage stress effectively. The intervention must have at most five clear steps and should follow this structured format:
        Format:
        1. **[Step Name] :** [Detailed description of what the user should do in this step, focusing on practicality and relevance to the stressor and location.]

        2. **[Step Name] :** [Detailed description of the next step.]
        ...

        End with a motivational concluding statement in one sentence summarizing the benefits of the intervention and providing encouragement.
        """
        
        interventions=get_responses(curr_prompt)
    else:        
        random_key = random.choice(list(intervention_steps_dict.keys()))
        random_value = intervention_steps_dict[random_key]
        interventions=random_value
    return intervention_type,interventions



    # <p style="margin-top: 10px;">
            #     Recently, you experienced a stress event due to <strong style="color: #e74c3c;">{info['Stressor']}</strong> 
            #     at <strong style="color: #e74c3c;">{info['Location']}</strong> on <strong style="color: #e74c3c;">{info['date']}</strong>.
            # </p>

def send_notification_email(subject, sender, receiver,receipient_name,receipient_uuid,date, info,intervention_type,interventions):
   

    sender_email = sender
    recipient_email = receiver
    subject = "Feedback on Stress Intervention"


    mod_intervention_type=""
    if intervention_type=="Generic":
        mod_intervention_type="g"
    else:
        mod_intervention_type="t"

    long_url = generate_qualtrics_link_intervention(receipient_name,receipient_uuid,info["Stressor"], info["Location"], info["date"], interventions,mod_intervention_type)
    short_url = shorten_url(long_url)


    if info.get("Stressor") == "Event not found" and info.get("Location") == "Location not found":
        stressor_text = "Recently, you experienced a stress event."
    else:
        stressor_text = f"Recently, you experienced a stress event due to " \
                    f"<strong style='color: #e74c3c;'>{info.get('Stressor', 'an unspecified event')}</strong> " \
                    f"at <strong style='color: #e74c3c;'>{info.get('Location', 'an unspecified location')}</strong> " \
                    f"on <strong style='color: #e74c3c;'>{info.get('date', 'an unspecified date')}</strong>."

    html_content=f"""

<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;">
            
            <!-- Header -->
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #2c3e50;">Your Personalized Support Insights</h2>
            </div>
            
            <!-- Stressor Information -->
            <div style="background-color: #fff; padding: 20px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 20px;">
                <p style="font-size: 16px; margin: 0;">Dear <strong>{receipient_name}</strong>,</p>          
                <p style="margin-top: 10px;">{stressor_text}</p>
            </div>
            
            <!-- Suggested Intervention -->
            <div style="background-color: #e8f5e9; padding: 20px; border: 1px solid #c8e6c9; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #388e3c;">🌟 Suggested Intervention:</h3>
                <pre style="color: #2e7d32; background-color: #f1f8e9; padding: 10px; border-radius: 5px; font-size: 14px;">
{interventions}
                </pre>
            </div>
            
            <!-- Feedback Request -->
            <div style="background-color: #e3f2fd; padding: 20px; border: 1px solid #bbdefb; border-radius: 8px; margin-bottom: 20px; text-align: center;">
                <h3 style="color: #1976d2;">📢 We Need Your Feedback!</h3>
                <p style="font-size: 16px;">Please let us know how helpful this intervention was for you.</p>
                <a href="{short_url}" style="display: inline-block; padding: 12px 24px; font-size: 18px; color: white; background-color: #0288d1; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                    👉 Share Your Feedback
                </a>
            </div>
            
            <!-- Closing Note -->
            <div style="text-align: center; margin-top: 20px;">
                <p style="font-size: 16px; margin-bottom: 5px;">Thank you for contributing to this important initiative. Your insights are invaluable!</p>
                <p>Warm regards,</p>
                <p><strong>The Relief Study Team</strong></p>
                <p><strong> The mDOT Center</strong></p>
                <p><strong>University of Memphis</strong></p>
   
    
            </div>
            
            <!-- Footer -->
            <hr style="margin: 20px 0;">
            <p style="font-size: 12px; color: #7f8c8d; text-align: center;">
                If you have any questions, feel free to reply to this email or contact us at 
                <a href="mailto:reliefmdot@gmail.com" style="color: #007bff;">reliefmdot@gmail.com</a>.
            </p>
        </div>
    </body>
</html>

"""


    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient_email
        # print(sender_email,recipient_email)
        # Attach the HTML content
        msg.attach(MIMEText(html_content, "html"))

        # Send the email
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:  # Replace with your SMTP server
            # server.starttls()
            server.login(EMAIL_ADDRESS, PASSWORD)  # Replace with your credentials
            server.send_message(msg)

        print("Email sent successfully!")
    except Exception as e:
        print("Error : Failed to send error " + e)



def check_email_for_subject():
    """Check inbox for emails with a specific subject line."""
    try:
            
        current_datetime = datetime.now()
        print(f"Current Date and Time: {current_datetime}") 
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, PASSWORD)
        mail.select("inbox")
        
        # mail_ids=[]
        # for i in SEARCH_SUBJECT:
        #     status, messages = mail.search(None, f'SUBJECT "{i}"')
        #     ids = messages[0].split()
        #     mail_ids.extend(ids)
        # status, messages = mail.search(None, f'SUBJECT "{SEARCH_SUBJECT}"')
        # mail_ids = messages[0].split()
        # print(len(mail_ids))
        # mail_ids.reverse()
        # print(mail_ids)
        
        for search_text in SEARCH_SUBJECT:
            outer_break = 0
            print(search_text)
            status, messages = mail.search(None, f'SUBJECT "{search_text}"')
            mail_ids = messages[0].split()
            mail_ids.reverse()
            for mail_id in mail_ids:
                # print("Email Found: Checking new or not")
                status, msg_data = mail.fetch(mail_id, '(RFC822)')
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        email_subject = msg['subject']
                        email_from = msg['from'].lower()
                        email_date = msg['Date']
                        # print(msg.keys())
                        # print(email_from)
                        if email_from not in participant_hashmap:
                            print("Email address not a registered user", email_from)
                            continue

                        email_id = msg['Message-ID']
                        if not email_id:
                            print("No Message-ID found, skipping email.")
                            continue
                        # print(msg["from"])
                        # print(f"Email Message-ID: {email_id}")
                        # if not email_subject.startswith(SEARCH_SUBJECT):
                        # if SEARCH_SUBJECT not in email_subject:
                        # for i in SEARCH_SUBJECT:
                        #     if i not in email_subject:
                        #         # print(email_id)
                        #         continue 

                        if search_text not in email_subject:
                            print(email_id)
                            continue 
                        
                        try:
                            email_datetime = datetime.strptime(email_date, '%a, %d %b %Y %H:%M:%S %z')
                            email_datetime = email_datetime.isoformat()
                        except ValueError:
                            print(f"Error parsing email date: {email_date}")
                            continue
                        
                        if email_already_processed(email_id):
                            print("Email already checked",email_from,email_datetime)
                            outer_break+=1
                            break  
                        else:

                            print("New email",email_from,email_datetime)
                            
                            sender_folder = os.path.join(ATTACHMENTS_FOLDER, re.sub(r'[<>:"/\\|?*]', '_', email_from))
                            # print(sender_folder,email_from)
                            os.makedirs(sender_folder, exist_ok=True)
                            
                            try:
                                
                                if msg.is_multipart():
                                    
                                    for part in msg.walk():
                                        
                                        content_type = part.get_content_type()
                                        
                                        if content_type == "text/html":
                                            html_content = part.get_payload(decode=True).decode()
                                        
                
                                    # Save images from email, now including attachments
                                    info=save_images_from_email(sender_folder, msg, email_from, email_date)
                                else:
                                    
                                    html_content = msg.get_payload(decode=True).decode()
                        
                                    info=save_images_from_email(sender_folder, msg, email_from, email_date)
                            except Exception as e:
                                print(f"something wrong with email: {e}")
                                continue
                            

                            receipient_name=""
                            receipient_uuid=""
                            for id in participant_hashmap:
                                if id in email_from:
                                    receipient_name=participant_hashmap[id][1]
                                    receipient_uuid=participant_hashmap[id][0]
                            
                            # print(info)
                            # print(mail_id, email_from, email_date, info)
                            
                            if len(info)==0:
                                info["Stressor"]="Event not found"
                                info["Location"]="Location not found"
                                info["date"]=""
                                info["valence"]=""
                                save_extracted_words_all(email_id, email_from,receipient_name, receipient_uuid, email_date,info, "","")

                                intervention_type,interventions=create_prompt(info)
                                send_notification_email(email_subject, EMAIL_ADDRESS, email_from,receipient_name,receipient_uuid,email_date, info,intervention_type,interventions)


                                save_email_id(email_id,email_datetime,email_from,receipient_name,receipient_uuid,"No stressor found (No image)","No Date found (No image)")
                                
                                continue    

                            if stressor_already_processed(receipient_uuid,info["Stressor"], info["date"]):
                                print("Stressor already processed",email_from,email_datetime)
                                save_extracted_words_all(email_id, email_from,receipient_name, receipient_uuid, email_date, info,"","")
                                save_email_id(email_id,email_datetime,email_from,receipient_name,receipient_uuid,info["Stressor"],info["date"])
                                
                                
                            else:
                                intervention_type,interventions=create_prompt(info)
                                save_extracted_words_intervention(email_id, email_from,receipient_name, receipient_uuid, email_date, info,intervention_type,interventions)                  
                                save_extracted_words_all(email_id, email_from,receipient_name, receipient_uuid, email_date, info,intervention_type,interventions)

                                send_notification_email(email_subject, EMAIL_ADDRESS, email_from,receipient_name,receipient_uuid,email_date, info,intervention_type,interventions)
                                save_email_id(email_id,email_datetime,email_from,receipient_name,receipient_uuid,info["Stressor"],info["date"])

                        # return email_subject, email_from,receipient_name, email_date, info,intervention_type,interventions
                if outer_break==5:
                    print("Email already checked found five times : Hence Stopping")
                    break
    except Exception as e:
        print(f"Error checking email: {e}")


print("\n")
print("Process started")

setup_databases()

my_database_paths = [
       FOUND_EMAILS_DB,       
       EXTRACTED_WORDS_INTERVENTION_DB,
       EXTRACTED_WORDS_ALL_DB
    ]
backup_databases(my_database_paths)

check_email_for_subject()
database_csv(database_path=EXTRACTED_WORDS_INTERVENTION_DB,csv_file_name=extracted_csv_path)
database_csv(database_path=EXTRACTED_WORDS_ALL_DB,csv_file_name=all_extracted_csv_path)
print("Process finished")



        
   