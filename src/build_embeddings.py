from txtai.embeddings import Embeddings
import csv
import json


def get_vulnerabilities():
    # The path to your CSV file
    csv_file_path = 'vulnerabilities_cleaned.csv'

    # Initialize an empty list to hold the JSON structure
    json_list = []

    try:
        # Open the CSV file for reading
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            # Use the csv.DictReader to automatically use the first row as fieldnames
            csv_reader = csv.DictReader(csv_file)

            # Loop over each row in the CSV file
            for idx, row in enumerate(csv_reader, start=1):
                # Convert the current row to a dictionary, and add an 'id' field
                row_dict = {
                    'id': idx,
                    'secure_code': row['secure_code'],
                    'description': row['description'],
                    'secure_code': row['secure_code']
                }

                json_list.append(row_dict)

        return json_list

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    # Create an instance of Embeddings
    embeddings = Embeddings({"method": "transformers", "path": "sentence-transformers/all-MiniLM-L6-v2"})

    # Your dataset of vulnerabilities and hacks
    data = get_vulnerabilities()

    # Concatenate the fields and index the documents
    for item in data:
        # Create a single text string for each document
        document_text = f"Code Snippet: {item['secure_code']} Description: {item['description']} secure_code: {item['secure_code']}"

        print(document_text)

        print(item['id'])
        # Add the document to the index
        embeddings.index([(int(item['id']), document_text, None)])

    # Save the index to a file
    embeddings.save("vulnerabilities-index")


if __name__ == "__main__":
    main()