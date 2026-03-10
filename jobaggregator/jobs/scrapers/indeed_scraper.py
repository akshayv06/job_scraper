import cloudscraper
from bs4 import BeautifulSoup

def scrape_indeed():

    url = "https://in.indeed.com/q-java-backend-developer-jobs.html"

    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)

    print("Status:", response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []

    for job in soup.select("a.tapItem"):

        title_tag = job.select_one("h2.jobTitle")
        company_tag = job.select_one("span.companyName")
        location_tag = job.select_one("div.companyLocation")

        title = title_tag.text.strip() if title_tag else None
        company = company_tag.text.strip() if company_tag else None
        location = location_tag.text.strip() if location_tag else None

        job_url = "https://in.indeed.com" + job.get("href")

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "source": "Indeed",
            "url": job_url
        })

    print("Jobs scraped:", len(jobs))

    return jobs