import requests

def scrape_remoteok():

    url = "https://remoteok.com/api"

    response = requests.get(url)

    data = response.json()

    jobs = []

    for job in data[1:]:   # first item metadata hota hai

        jobs.append({
            "title": job.get("position"),
            "company": job.get("company"),
            "location": job.get("location"),
            "source": "RemoteOK",
            "url": job.get("url")
        })

    print("Jobs scraped:", len(jobs))

    return jobs