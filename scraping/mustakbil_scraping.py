from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import time, json, html

search_query = "ui designer"
url = f"https://www.mustakbil.com/jobs/search?countryid=162&keywords={search_query.replace(' ', '%20')}"

driver = webdriver.Chrome()
driver.get(url)
time.sleep(3)  # wait for JS to load

soup = BeautifulSoup(driver.page_source, "html.parser")

# --- Find all job cards ---
job_cards = soup.select("div.mat-card.list-item-hover")

# --- Lists for data ---
titles = []
companies = []
experiences = []
short_descriptions = []
locations = []
dates_posted = []
urls = []
full_descriptions = []
dates_scraped = []

for job_card in job_cards:
    try:
        # Title
        job_title = job_card.find("h3").get_text(strip=True)

        # URL
        job_url = "https://www.mustakbil.com" + job_card.find("a", href=True)["href"]

        # Company
        company = job_card.find("div", class_="company-name").get_text(strip=True)

        # Chips → Experience
        chips = job_card.find_all("div", class_="mat-chip")
        experience = ""
        for chip in chips:
            if "Year" in chip.get_text():
                experience = chip.get_text(strip=True)
                break

        # Short description (cleaned)
        job_desc_short = job_card.find("div", class_="mt10 mb10 paragraph")
        if job_desc_short:
            raw_text = job_desc_short.get_text(" ", strip=True)
            job_desc_short = html.unescape(" ".join(raw_text.split()))
        else:
            job_desc_short = ""

        # Location
        location_div = job_card.find("div", class_="flex flex-100-xs flex-center-y")
        location = location_div.get_text(strip=True) if location_div else ""

        # --- Open job detail page ---
        driver.get(job_url)
        time.sleep(3)
        soup_detail = BeautifulSoup(driver.page_source, "html.parser")

        # --- Full description ---
        description_text = ""
        desc_header = soup_detail.find("h2", class_="section-title", string="Job Description")
        if desc_header:
            desc_div = desc_header.find_next("div", class_="section-content")
            if desc_div:
                description_text = desc_div.get_text(" ", strip=True)

        # --- Date posted ---
        date_posted_clean = ""
        labels = soup_detail.find_all("div", class_="grid-label")
        for lbl in labels:
            if "Posted on" in lbl.get_text(strip=True):
                val_div = lbl.find_next("div", class_="grid-value")
                if val_div:
                    raw_date = val_div.get_text(strip=True)
                    date_posted_clean = datetime.strptime(raw_date, "%b %d, %Y").strftime("%Y-%m-%d")
                break

        # Date scraped
        date_scraped = datetime.today().strftime('%Y-%m-%d')

        # --- Save in lists ---
        titles.append(job_title)
        companies.append(company)
        experiences.append(experience)
        short_descriptions.append(job_desc_short)
        locations.append(location)
        dates_posted.append(date_posted_clean)
        urls.append(job_url)
        full_descriptions.append(description_text)
        dates_scraped.append(date_scraped)

    except Exception as e:
        print(f"Error processing job card: {e}")

driver.quit()

# Print all jobs scraped
for i in range(len(titles)):
    print(f"Job {i+1}:")
    print("Title:", titles[i])
    print("Company:", companies[i])
    print("Experience:", experiences[i])
    print("Short Description:", short_descriptions[i])
    print("Location:", locations[i])
    print("Date Posted:", dates_posted[i])
    print("URL:", urls[i])
    print("Full Description:", full_descriptions[i])
    print("Date Scraped:", dates_scraped[i])
    print("-" * 80)
