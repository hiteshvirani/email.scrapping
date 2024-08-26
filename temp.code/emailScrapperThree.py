import time
import re
import os
import pandas as pd
import ctypes
import tkinter as tk
from bs4 import BeautifulSoup
from tkinter import simpledialog
from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import sys

class EmailScrapper:

    def __init__(self, query, DEBUG=False, user_data_dir=None, profile_directory=None):
        self.emails = []
        self.email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

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
        self.driver.get(f'https://www.google.com/search?q={query}')

        try:
            # Clicking Ok on Cookies Acceptance of Google Search Engine
            self.driver.find_element(By.XPATH, '//*[@id="W0wltc"]').click() # At least for Germany
        except:
            pass
        time.sleep(1)
        self._find_emails()

    def _find_emails(self):
        soup = BeautifulSoup(self.driver.page_source, features="lxml")
        tmp = re.findall(self.email_regex, soup.text)
        self.emails.extend(tmp)
        time.sleep(1)
        self._next_page()

    def _next_page(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, '#pnnext span').click()
            time.sleep(3)
            self._find_emails()
        except:
            self._close()

    def _close(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        df = pd.DataFrame(self.emails, columns=['Emails'])
        df.index += 1
        df.to_csv(f'Scrapped-Emails-{timestamp}.csv', index_label='Sr No.')
        self.driver.close()

def run_ui(user_data_dir=None, profile_directory=None):
    # Create a new window for the custom dialog
    root = tk.Tk()
    email_scrapper_app = 'EmailScrapper'

    # Only set the AppUserModelID on Windows
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(email_scrapper_app)

    root.title("Email Scrapper")
    root.geometry("400x250")  # Set the size of the dialog window
    # root.iconbitmap('email_scrapper.ico')

    # Label
    label = tk.Label(root, text="Make Sure it shouldn't be covered with \"\"", font=('Arial', 8, 'italic'))
    label.pack(pady=10)
    label = tk.Label(root, text="Enter the Search Query:")
    label.pack(pady=10)

    # Text area (Entry widget with a larger size)
    query_var = tk.StringVar()
    query_entry = tk.Entry(root, textvariable=query_var, width=40, font=('Arial', 12))
    query_entry.pack(pady=10)

    # OK button
    def on_ok():
        query = query_var.get()
        if not query:
            error_label = tk.Label(root, text="Error: Query cannot be empty!", font=('Arial', 10, 'italic'), fg="red")
            error_label.pack(pady=20)
        else:
            root.destroy()
            EmailScrapper(query, user_data_dir=user_data_dir, profile_directory=profile_directory)

    ok_button = tk.Button(root, text=" OK ", command=on_ok)
    ok_button.pack(pady=10)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    user_data_dir = "/home/hitesh/.config/google-chrome"
    profile_directory = "Profile 13"
    run_ui(user_data_dir=user_data_dir, profile_directory=profile_directory)
