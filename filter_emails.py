import os
import csv
import re
from pathlib import Path

# Configuration
OUTPUT_FOLDER = 'output'
EMAILS_FOLDER = 'emails'
OUTPUT_CSV_NAME = 'extracted_emails.csv'

def setup_directories():
    """Create necessary directories"""
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(EMAILS_FOLDER, exist_ok=True)

def is_valid_email(email):
    """Check for valid Gmail address"""
    if not email:
        return False
    # Regex to check for a valid Gmail address
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email)) and '%' not in email

def extract_location_from_filename(filename):
    """Extract location from filename (handling various query formats)"""
    # Assuming filename format: site-linkedin-com-new-york-gmail-com_count.csv
    try:
        parts = filename.split('-')
        # This logic assumes the structure from generate.query.py roughly
        # It's a heuristic validation.
        # Let's try to find city name which is usually before the email part
        return filename.split('_')[0].replace('-', ' ')
    except:
        return 'Unknown'

def get_last_serial_number(filepath):
    """Get the last serial number from the CSV"""
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, 'r', newline='', encoding='utf-8') as file:
            reader = list(csv.reader(file))
            if len(reader) > 1:
                return int(reader[-1][0])
    except:
        pass
    return 0

def process_emails(output_path, input_folder):
    """Process scraped files and consolidate emails"""
    print(f"Processing files from {input_folder} to {output_path}...")
    
    file_exists = os.path.exists(output_path)
    existing_emails = set()
    
    # Load existing emails
    if file_exists:
        try:
            with open(output_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip header
                for row in reader:
                    if len(row) > 1:
                        existing_emails.add(row[1])
        except Exception as e:
            print(f"Error reading existing file: {e}")

    # Process new files
    processed_count = 0
    start_serial = get_last_serial_number(output_path) + 1
    
    with open(output_path, 'a', newline='', encoding='utf-8') as output_file:
        writer = csv.writer(output_file)
        
        if not file_exists:
            writer.writerow(['Sr No.', 'Emails', 'Location'])
        
        files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
        print(f"Found {len(files)} files to process.")
        
        for filename in files:
            file_path = os.path.join(input_folder, filename)
            location = extract_location_from_filename(filename)
            
            try:
                with open(file_path, mode='r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader, None)  # Skip header
                    
                    file_emails = 0
                    for row in reader:
                        if len(row) < 2:
                            continue
                            
                        email = row[1]
                        if is_valid_email(email) and email not in existing_emails:
                            writer.writerow([start_serial, email, location])
                            existing_emails.add(email)
                            start_serial += 1
                            file_emails += 1
                            processed_count += 1
                    
                # Delete processed file
                os.remove(file_path)
                print(f"  Processed {file_emails} emails from {filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print(f"Done. Extracted {processed_count} new emails.")

def main():
    setup_directories()
    output_path = os.path.join(EMAILS_FOLDER, OUTPUT_CSV_NAME)
    process_emails(output_path, OUTPUT_FOLDER)

if __name__ == "__main__":
    main()