import openai
from openai import OpenAI

IMAP_SERVER = 'imap.gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT=465
EMAIL_ADDRESS = 'reliefmdot@gmail.com'
# PASSWORD = '' # mero gmail ko password
PASSWORD = ''

client = OpenAI(api_key="")


def get_responses(prompts):
    # responses={}
    
    # print(prompts)
    completion = client.chat.completions.create(
      model = 'gpt-4o',
      messages = [
        {'role': 'user', 'content':prompts}
      ],
      temperature = 0  ,
        max_tokens=500
    )

    generated_text = completion.choices[0].message.content
    return generated_text
    # print("Prompt : "+ prompts)
    # print("\n")
    # print("Response \n" +generated_text)
    # # responses[c]=generated_text
    # print("-------------------------------------------")