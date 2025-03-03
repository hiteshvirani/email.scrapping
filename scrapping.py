import time
import re
import os
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller

class EmailScraper:
    def __init__(self, query, query_name, csv_path, row_index, DEBUG=True, user_data_dir=None, profile_directory=None):
        self.query = query
        self.query_name = query_name
        self.csv_path = csv_path
        self.row_index = row_index
        self.emails = []
        self.email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        self.page_number = 1
        self.found_emails = False  # Track if any emails are found

        chromedriver_autoinstaller.install()
        options = webdriver.ChromeOptions()

        if DEBUG:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        if user_data_dir:
            options.add_argument(f"user-data-dir={user_data_dir}")
        if profile_directory:
            options.add_argument(f"profile-directory={profile_directory}")

        options.add_argument("--disable-search-engine-choice-screen")
        options.add_experimental_option("prefs", {"profile.default_content_settings.cookies": 2})
        self.driver = webdriver.Chrome(options=options)
        self._scrape()

    def _scrape(self):
        try:
            self.driver.get(f'https://www.google.com/search?q={self.query}')
            # Attempt to click the "Accept Cookies" button
            try:
                self.driver.find_element(By.XPATH, '//*[@id="W0wltc"]').click()
            except Exception:
                print("Cookie acceptance button not found or already accepted.")

            time.sleep(random.randrange(25, 80))
            self._find_emails()
            self._save_emails_to_csv()
        finally:
            self._update_csv_status()  # Update CSV status after scraping
            self.driver.quit()

    def _find_emails(self):
        while True:
            soup = BeautifulSoup(self.driver.page_source, features="lxml")
            emails_on_page = re.findall(self.email_regex, soup.text)
            if emails_on_page:
                self.found_emails = True  # Set flag to True if any emails are found
            self.emails.extend(emails_on_page)
            print(f"Page {self.page_number}: Found {len(emails_on_page)} emails.")

            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, '#pnnext span')
                next_button.click()
                self.page_number += 1
                time.sleep(random.randrange(25, 80))
            except:
                print("No more pages to scrape.")
                break

    def _save_emails_to_csv(self):
        # output_dir = "/app/output"
        output_dir = "/home/hitesh/A/Data/email.scrapping/output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        query_name = re.sub(r'[\W_]+', '-', self.query_name.lower())
        random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=3))
        file_name = f"{output_dir}/{query_name}_{random_suffix}.csv"

        if self.emails:
            df = pd.DataFrame(self.emails, columns=['Emails'])
            df.index += 1
            df.to_csv(file_name, index_label='Sr No.')
            print(f"Saved {len(self.emails)} emails to {file_name}.")
        else:
            print(f"No emails found for query: {self.query_name}. CSV file still generated.")

    def _update_csv_status(self):
        if self.found_emails:
            # Load the CSV file into a DataFrame
            df = pd.read_csv(self.csv_path, header=None)
            # Drop the row at the specified index
            df = df.drop(self.row_index)
            # Reset the index to keep it consistent
            df = df.reset_index(drop=True)
            # Save the updated DataFrame back to the CSV file
            df.to_csv(self.csv_path, header=None, index=False)
            print(f"Removed row {self.row_index} from CSV because emails were found.")
        else:
            print(f"No emails found for query: {self.query_name}. Row {self.row_index} not removed.")

def run_scraper(csv_path, user_data_dir=None, profile_directory=None):
    df = pd.read_csv(csv_path, header=None)

    if df.empty:
        print("No more columns to scrape.")
        return

    for index, row in df.iterrows():
        query = row[1]
        query_name = query.replace('"', '').replace(' ', '_')
        if len(row) < 3 or pd.isna(row[2]):
            EmailScraper(query, query_name, csv_path, index, user_data_dir=None, profile_directory=profile_directory)

if __name__ == "__main__":
    print('Scraping main method...')
    # csv_path = os.getenv('CSV_PATH', '/app/input/default.csv')  # Use for multiple Docker container running
    csv_path = '/home/hitesh/A/Data/email.scrapping/input/search.queries.1.csv'
    print(f'csv_path: {csv_path}')
    user_data_dir = "/root/.config/google-chrome"  # Default Chrome user data directory in Docker
    profile_directory = "Profile 13"
    run_scraper(csv_path, user_data_dir=user_data_dir, profile_directory=profile_directory)
