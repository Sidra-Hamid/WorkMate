from bs4 import BeautifulSoup
from selenium import webdriver
import time
from datetime import date
import urllib.parse

# --- Selenium setup ---
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


base_url = "https://www.rozee.pk/job/jsearch/q/"
query = "ui designer"
encoded_query = urllib.parse.quote(query) # encode to handle spaces

url = base_url + encoded_query

driver.get(url)
time.sleep(3)

soup = BeautifulSoup(driver.page_source, "html.parser")

# --- Locate job cards ---
job_cards = soup.select("#jobs .job")

# --- Lists to store scraped data ---
titles, companies, locations, links = [], [], [], []
preview_descs, full_descs = [], []
dates_posted, experiences, skills_list, dates_scraped = [], [], [], []

# --- Loop through jobs ---
for job in job_cards:
    # Job title & link
    title_tag = job.select_one("h3.s-18 a")
    title = title_tag.get_text(strip=True) if title_tag else None
    link = title_tag["href"] if title_tag else None
    if link and link.startswith("//"):
        link = "https:" + link

    # Company & location
    company_block = job.select_one(".cname")
    company, location = None, None
    if company_block:
        parts = [p.strip() for p in company_block.get_text(" ", strip=True).split(",")]
        company = parts[0] if len(parts) > 0 else None
        location = ", ".join(parts[1:]) if len(parts) > 1 else None

    # Preview description
    desc_tag = job.select_one(".jbody bdi")
    preview_desc = desc_tag.get_text(strip=True) if desc_tag else None

    # Date posted
    date_tag = job.select_one(".jfooter .rz-calendar")
    date_posted = date_tag.find_parent("span").get_text(strip=True) if date_tag else None

    # Experience
    exp_tag = job.select_one(".func-area-drn")
    experience = exp_tag.get_text(strip=True) if exp_tag else None

    # Skills
    skill_tags = job.select(".jfooter .label")
    skills = [s.get_text(strip=True) for s in skill_tags]

    # Full description (navigate into job link)
    full_desc = None
    if link:
        driver.get(link)
        time.sleep(2)
        detail_soup = BeautifulSoup(driver.page_source, "html.parser")
        desc_container = detail_soup.select_one("div.jblk.ul18 div[dir='ltr']")
        if desc_container:
            for br in desc_container.find_all("br"):
                br.replace_with(" ")
            full_desc = desc_container.get_text(" ", strip=True)

    # Append to lists
    titles.append(title)
    companies.append(company)
    locations.append(location)
    links.append(link)
    preview_descs.append(preview_desc)
    full_descs.append(full_desc)
    dates_posted.append(date_posted)
    experiences.append(experience)
    skills_list.append(skills)
    dates_scraped.append(date.today().strftime("%Y-%m-%d"))

# --- Display scraped results ---
for i in range(len(titles)):
    print(f"Title: {titles[i]}")
    print(f"Company: {companies[i]}")
    print(f"Location: {locations[i]}")
    print(f"Link: {links[i]}")
    print(f"Preview Desc: {preview_descs[i]}")
    print(f"Full Desc: {full_descs[i][:200] if full_descs[i] else None}...")  # preview first 200 chars
    print(f"Date Posted: {dates_posted[i]}")
    print(f"Experience: {experiences[i]}")
    print(f"Skills: {skills_list[i]}")
    print(f"Date Scraped: {dates_scraped[i]}")
    print("=" * 80)

driver.quit()