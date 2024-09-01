import os
import csv
import re

def extract_emails(folder_path, output_csv_path, check_duplicates=True):
    # Ensure continuous serial numbers and unique emails if the output file already exists and flag is true
    if os.path.isfile(output_csv_path) and check_duplicates:
        remove_duplicates_and_make_serial_numbers_continuous(output_csv_path)

    # Check if the output file exists after the above operation
    file_exists = os.path.isfile(output_csv_path)

    # Set to keep track of existing emails
    existing_emails = set()

    if file_exists:
        # Load existing emails into the set
        with open(output_csv_path, 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                existing_emails.add(row[1])

    with open(output_csv_path, 'a', newline='') as output_file:
        writer = csv.writer(output_file)

        # Write the header if the file does not exist
        if not file_exists:
            writer.writerow(['Sr No.', 'Emails', 'Location'])

        # Determine the starting serial number for appending new entries
        start_serial_no = get_last_serial_number(output_csv_path) + 1

        # Walk through the files in the folder
        for filename in os.listdir(folder_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(folder_path, filename)
                location = extract_location_from_filename(filename)

                with open(file_path, mode='r') as file:
                    reader = csv.reader(file)
                    next(reader)  # Skip header row

                    for row in reader:
                        email = row[1]
                        if is_valid_email(email) and email not in existing_emails:
                            writer.writerow([start_serial_no, email, location])
                            existing_emails.add(email)
                            start_serial_no += 1

                # Delete the old CSV file
                os.remove(file_path)

def remove_duplicates_and_make_serial_numbers_continuous(output_csv_path):
    # Read the existing CSV and remove duplicate emails
    with open(output_csv_path, 'r', newline='') as file:
        reader = list(csv.reader(file))

    # Skip the header and ensure emails are unique
    header, rows = reader[0], reader[1:]
    unique_rows = []
    seen_emails = set()

    for row in rows:
        if row[1] not in seen_emails:
            unique_rows.append(row)
            seen_emails.add(row[1])

    # Correct serial numbers
    for i, row in enumerate(unique_rows):
        row[0] = i + 1

    # Write the updated rows back to the CSV
    with open(output_csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(unique_rows)

def get_last_serial_number(output_csv_path):
    # Get the last serial number from the output CSV
    with open(output_csv_path, 'r', newline='') as file:
        reader = list(csv.reader(file))
        if len(reader) > 1:
            return int(reader[-1][0])
        else:
            return 0

def is_valid_email(email):
    # Regex to check for a valid Gmail address and ignore those with % signs
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email)) and '%' not in email

def extract_location_from_filename(filename):
    # Extract the location from the filename
    parts = filename.split('-')
    if len(parts) > 2:
        location = parts[-3].replace('-', ' ')
    else:
        location = 'Unknown'
    return location

# Set your folder path and output CSV path here
folder_path = '/home/hitesh/A/Data/email.scrapping/output'
output_csv_path = '/home/hitesh/A/Data/email.scrapping/emails/extracted_emails.csv'

# Set the flag for checking duplicates in the existing CSV
check_duplicates_flag = True

extract_emails(folder_path, output_csv_path, check_duplicates_flag)