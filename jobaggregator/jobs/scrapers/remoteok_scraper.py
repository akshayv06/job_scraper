import requests

def scrape_remoteok():

    url = "https://remoteok.com/api"

    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    data = response.json()

    jobs = []

    for job in data[1:]:

        description = job.get("description", "")
        tags = job.get("tags", [])

        jobs.append({
            "title": job.get("position"),
            "company": job.get("company"),
            "location": job.get("location", "Remote"),
            "source": "RemoteOK",
            "url": job.get("url"),
            
            # 🔥 NEW FIELDS (VERY IMPORTANT)
            "description": description,
            "skills": tags,   # RemoteOK tags = skills
            "experience_level": job.get("experience", "Not specified")
        })

    print("Jobs scraped:", len(jobs))

    return jobs