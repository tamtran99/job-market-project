
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import psycopg2

# 🔹 Thông tin tìm kiếm
title = "Data Analyst"  # Tiêu đề công việc
location = "Ho Chi Minh City"  # Địa điểm
start = 0  # Pagination (bắt đầu từ 0)
id_set = set()  # Danh sách ID job


MAX_JOBS = 50  # Giới hạn số lượng job



# 🔹 Cấu hình PostgreSQL
# DB_CONFIG_OLD = {
#     "dbname": "linkedin_project",
#     "user": "postgres",
#     "password": "141099",
#     "host": "localhost",
#     "port": "5432"
# }

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres.esuhrzsmhlzrvgrkwmop",
    "password": "EWr9AInpTmKi1uwa",
    "host": "aws-0-ap-southeast-1.pooler.supabase.com",
    "port": "6543"
}

while len(id_set) < MAX_JOBS:
    list_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&start={start}"
    response = requests.get(list_url)

    # Check if the response is invalid or no more jobs are found
    if response.status_code != 200 or not response.text:
        print("No more jobs found, stopping...")
        break

    list_soup = BeautifulSoup(response.text, "html.parser")
    page_jobs = list_soup.find_all("li")

    if not page_jobs:
        print("No more job postings available.")
        break

    for job in page_jobs:
        base_card_div = job.find("div", {"class": "base-card"})
        if base_card_div:
            job_id = base_card_div.get("data-entity-urn").split(":")[3]
            id_set.add(job_id)  # Using a set ensures duplicate job IDs are automatically filtered out

    print(f"Fetched {len(id_set)} unique job IDs so far...")

    start += 10  # Increase page index by 10 (LinkedIn shows 10 jobs per request)
    time.sleep(2)  # Avoid being blocked by too many requests

# Convert the set to a list for further processing
id_list = list(id_set)
print(f"✅ Total unique jobs collected: {len(id_list)}")
print(id_list)


# 🔹 Lấy thông tin chi tiết từng job
job_list = []

for job_id in id_list:
    job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    job_response = requests.get(job_url)
    
    if job_response.status_code != 200:
        print(f"⚠️ Failed to fetch job {job_id}")
        continue

    job_soup = BeautifulSoup(job_response.text, "html.parser")

    job_post = {}

    job_post = {"job_id": job_id}  # Thêm Job ID vào dict
    
    try:
        job_post["job_title"] = job_soup.find("h2", {"class": "top-card-layout__title"}).text.strip()
    except:
        job_post["job_title"] = None

    try:
        job_post["company_name"] = job_soup.find("a", {"class": "topcard__org-name-link"}).text.strip()
    except:
        job_post["company_name"] = None

    try:
        job_post["location"] = job_soup.find("span", {"class": "topcard__flavor topcard__flavor--bullet"}).text.strip()
    except:
        job_post["location"] = None

    try:
        job_post["time_posted"] = job_soup.find("span", {"class": "posted-time-ago__text"}).text.strip()
    except:
        job_post["time_posted"] = None

    try:
        job_post["num_applicants"] = job_soup.find("span", {"class": "num-applicants__caption"}).text.strip()
    except:
        job_post["num_applicants"] = None
    try:
        job_desc_div = job_soup.find("div", class_="show-more-less-html__markup")
        job_post["description"] = job_description = job_desc_div.get_text(separator="\n").strip()
    except:
        job_post["description"] = None


    job_list.append(job_post)
    time.sleep(1)  # Tránh bị chặn request

def insert_into_postgres(job_list):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()


    insert_query = """
    INSERT INTO crawl_linkedin.linkedin_data_raw (job_id, job_title, company_name, location, time_posted, num_applicants, description)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    
    """
    for job in job_list:
        cursor.execute(insert_query, (
            job["job_id"],
            job["job_title"],
            job["company_name"],
            job["location"],
            job["time_posted"],
            job["num_applicants"],
            job["description"]
        ))

    conn.commit()
    cursor.close()
    conn.close()

insert_into_postgres(job_list) #Call function
print("✅ Data inserted successfully!")