import os
import time
import re
import requests
import shutil
import streamlit as st
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

if not GROQ_API_KEY:
    st.error("Error: GROQ_API_KEY is not set. Create a `.env` file and add your API key.")
    st.stop()

# Set up Selenium options
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    chrome_path = shutil.which("chromium") or shutil.which("google-chrome")
    driver_path = shutil.which("chromedriver")

    if not chrome_path or not driver_path:
        raise Exception("Chromium or ChromeDriver is missing. Install them before running.")

    service = Service(driver_path)
    return webdriver.Chrome(service=service, options=options)

# Function to scrape Instagram comments
def scrape_instagram_comments(reel_url):
    driver = get_driver()
    driver.get(reel_url)
    time.sleep(5)

    comments = []
    try:
        comments_elements = driver.find_elements(By.CSS_SELECTOR, "ul li span")
        comments = [comment.text for comment in comments_elements if comment.text.strip()]
    except Exception as e:
        st.error(f"Error scraping Instagram: {e}")

    driver.quit()
    return comments

# Function to scrape YouTube comments
def scrape_youtube_comments(video_url):
    driver = get_driver()
    driver.get(video_url)
    time.sleep(5)

    comments = []
    try:
        body = driver.find_element(By.TAG_NAME, "body")

        for _ in range(8):  
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(2)

        comments_elements = driver.find_elements(By.CSS_SELECTOR, "#content-text")
        comments = [comment.text for comment in comments_elements if comment.text.strip()]
    except Exception as e:
        st.error(f"Error scraping YouTube: {e}")

    driver.quit()
    return comments

# Function to clean comments
def clean_comment(comment):
    return re.sub(r'[^\w\s.,!?\'"-]', '', comment)

spam_keywords = ["follow me", "free money", "click this link", "DM us", "buy followers", "promotion", "promo code", "earn cash", "in
