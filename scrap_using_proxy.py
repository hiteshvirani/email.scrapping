import time
import re
import os
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import requests
from selenium.webdriver.chrome.options import Options


class EmailScraper:
    def __init__(self, query, query_name, csv_path, row_index, DEBUG=True, user_data_dir=None, profile_directory=None):
        self.query = query
        self.query_name = query_name
        self.csv_path = csv_path
        self.row_index = row_index
        self.emails = []
        self.email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        self.page_number = 1
        self.proxies = self._filter_proxies()
        self.driver = None

        chromedriver_autoinstaller.install()

        if DEBUG:
            self.options = Options()
            self.options.add_argument("--headless")
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-dev-shm-usage")
        else:
            self.options = webdriver.ChromeOptions()

        if user_data_dir:
            self.options.add_argument(f"user-data-dir={user_data_dir}")
        if profile_directory:
            self.options.add_argument(f"profile-directory={profile_directory}")

        self.options.add_argument("--disable-search-engine-choice-screen")
        self.options.add_experimental_option("prefs", {"profile.default_content_settings.cookies": 2})

        self._create_driver_with_proxy()
        self._scrape()

    def _filter_proxies(self):
        response = requests.get('https://www.sslproxies.org/')
        soup = BeautifulSoup(response.text, "html.parser")
        proxies = []
        for item in soup.select("table.table tbody tr"):
            if not item.select_one("td"):
                break
            ip = item.select_one("td").text
            port = item.select_one("td:nth-of-type(2)").text
            proxies.append(f"{ip}:{port}")
        return proxies

    def _create_driver_with_proxy(self):
        if not self.proxies:
            print("Proxies used up, fetching new ones.")
            self.proxies = self._filter_proxies()

        proxy = self.proxies.pop()
        self.options.add_argument(f'--proxy-server={proxy}')
        self.driver = webdriver.Chrome(options=self.options)
        print(f"Using proxy: {proxy}")

    def _scrape(self):
        try:
            while True:
                try:
                    self.driver.get(f'https://www.google.com/search?q={self.query}')
                    # Attempt to click the "Accept Cookies" button
                    try:
                        self.driver.find_element(By.XPATH, '//*[@id="W0wltc"]').click()
                    except Exception:
                        print("Cookie acceptance button not found or already accepted.")

                    time.sleep(random.uniform(5, 15))  # Reduce delay between requests
                    self._find_emails()
                    self._update_csv_status()
                    break
                except Exception as e:
                    print(f"Error: {e}. Switching proxy...")
                    self.driver.quit()
                    self._create_driver_with_proxy()
                    time.sleep(random.uniform(5, 10))  # Short delay before trying the next proxy
        finally:
            self._save_emails_to_csv()
            self.driver.quit()

    def _find_emails(self):
        while True:
            soup = BeautifulSoup(self.driver.page_source, features="lxml")
            emails_on_page = re.findall(self.email_regex, soup.text)
            self.emails.extend(emails_on_page)
            print(f"Page {self.page_number}: Found {len(emails_on_page)} emails.")

            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, '#pnnext span')
                next_button.click()
                self.page_number += 1
                time.sleep(random.uniform(7, 15))  # Reduce delay between page requests
            except:
                print("No more pages to scrape.")
                break

    def _save_emails_to_csv(self):
        output_dir = "/home/hitesh/A/Data/email.scrapping//output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        query_name = re.sub(r'[\W_]+', '-', self.query_name.lower())
        file_name = f"{output_dir}/{query_name}.csv"

        if self.emails:
            df = pd.DataFrame(self.emails, columns=['Emails'])
            df.index += 1
            df.to_csv(file_name, index_label='Sr No.')
            print(f"Saved {len(self.emails)} emails to {file_name}.")
        else:
            print(f"No emails found for query: {self.query_name}. CSV file still generated.")

    def _update_csv_status(self):
        df = pd.read_csv(self.csv_path, header=None)
        df = df.drop(self.row_index)
        df = df.reset_index(drop=True)
        df.to_csv(self.csv_path, header=None, index=False)
        print(f"Removed row {self.row_index} from CSV.")


def run_scraper(csv_path, user_data_dir=None, profile_directory=None):
    df = pd.read_csv(csv_path, header=None)

    for index, row in df.iterrows():
        query = row[1]
        query_name = query.replace('"', '').replace(' ', '_')
        if len(row) < 3 or pd.isna(row[2]):
            EmailScraper(query, query_name, csv_path, index, user_data_dir=None, profile_directory=profile_directory)


if __name__ == "__main__":
    print('Scraping main method....')
    # csv_path = os.getenv('CSV_PATH', '/app/input/default.csv') # Use for multiple docker container running
    csv_path = '/home/hitesh/A/Data/email.scrapping/input/search.queries.1.csv'
    print(f'CSV Path: {csv_path}')
    user_data_dir = "/root/.config/google-chrome"  # Default Chrome user data directory in Docker
    profile_directory = "Profile 13"
    run_scraper(csv_path, user_data_dir=user_data_dir, profile_directory=profile_directory)
