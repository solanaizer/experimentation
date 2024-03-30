import csv
import os
import dotenv
from src.ai_validator import ChatRequest
import requests
import regex as re

csv_file_path = 'vulnerabilities_full.csv'
dotenv.load_dotenv()


def get_examples():
    vulnerabilities = {}

    # Open the CSV file
    with open('vulnerabilities_full.csv', mode='r', encoding='utf-8') as csvfile:
        # Create a CSV reader object
        reader = csv.reader(csvfile)

        # Skip the header row if there is one
        next(reader, None)

        # Iterate over each row in the CSV file
        for row in reader:
            # Assuming the first column is the ID
            id = row[0]

            # Create a dictionary for the current row and exclude the ID from the values
            vulnerability_info = {
                'insecure_code': row[1],
                'description': row[2],
                'mitigation': row[3]
            }

            # Add the current row's data to the main dictionary with the ID as the key
            vulnerabilities[id] = vulnerability_info

    return vulnerabilities


def main():
    v_dict = get_examples()
    print(len(v_dict))

    messages = []

    for i in range(0, len(v_dict)):
        try:
            v = v_dict[str(i)]
            message = clean_data(v['description'], v['insecure_code'], v['mitigation'])
            messages.append(message)
        except:
            print("some issue occured: " + str(i))

    csv_file_name = 'vulnerabilities_cleaned.csv'

    with open(csv_file_name, mode='w', newline='', encoding='utf-8') as csvfile:
        # Create a CSV writer object
        writer = csv.writer(csvfile)

        # Write the header row based on the keys of your dictionary
        writer.writerow(['Description', 'Insecure Code', 'Secure Code'])

        # Iterate over each dictionary in your list and write it to the CSV file
        for message in messages:

            print(message)

            writer.writerow([message['description'], message['insecure'], message['secure']])


def extract_message_sections(message):
    # Define patterns to identify the start of each section
    description_pattern = re.compile(r'1\. Vulnerability Description:')
    insecure_code_pattern = re.compile(r'2\. Updated Insecure Code')
    secure_code_pattern = re.compile(r'3\. Updated Secure Code')

    # Split the message by lines
    lines = message.split('\n')

    # Initialize variables to hold the content of each section
    description = []
    insecure_code = []
    secure_code = []

    # Initialize a variable to keep track of the current section
    current_section = None

    # Iterate over each line in the message
    for line in lines:
        # Check if the line marks the start of a new section
        if description_pattern.match(line):
            current_section = 'description'
        elif insecure_code_pattern.match(line):
            current_section = 'insecure_code'
        elif secure_code_pattern.match(line):
            current_section = 'secure_code'
        else:
            # Add the line to the appropriate section based on the current_section value
            if current_section == 'description':
                description.append(line)
            elif current_section == 'insecure_code':
                insecure_code.append(line)
            elif current_section == 'secure_code':
                secure_code.append(line)

    # Join the lines in each section to form complete strings
    description_str = '\n'.join(description).strip()
    insecure_code_str = '\n'.join(insecure_code).strip()
    secure_code_str = '\n'.join(secure_code).strip()

    # Construct the final dictionary with the extracted content
    extracted_message = {
        'description': description_str,
        'insecure': insecure_code_str,
        'secure': secure_code_str
    }

    return extracted_message


def clean_data(description, insecure_code, secure_code):
    api_key = os.getenv("CHATGPT_API_KEY")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    prompt = f"""
    You are a super smart Solana AI smart contract auditor.
    
    I will give you a smart contract vulnerability description, the insecure code, and the corresponding secure code.
    
    I want you to remove any excess that is not needed from each piece of code, and simplify it to the root of the 
    problem. Think clearly and ensure that the final code does not resemble what we started with. Remove things which
    are not needed. Including parts necessary to make the code compile, after all this will just be used for 
    Retrieval Augmented Generation.
    
    Only reply with:
    
    1. Vulnerability Description:
    
    2. Updated Insecure Code
    ```rs
    'INSECURE CODE HERE`
    ```
    
    3. Updated Secure Code
    ```rs
    'SECURE CODE HERE`
    ```    
    
    The code to update starts now:
    
    Original Description : '{description}'
    
    Original Insecure Code: 
    ```rs
    {insecure_code}
    ```
    
    Original Secure Code:
    ```rs
    {secure_code}
    ```
    """

    chat_request = ChatRequest(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    response = requests.post(url, headers=headers, data=chat_request.toJSON())

    if response.ok:
        response_json = response.json()
        response_content = response_json["choices"][0]["message"]["content"]

        return extract_message_sections(response_content)


if __name__ == "__main__":
    main()
