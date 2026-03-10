from celery import shared_task
from .models import Job
from .scrapers.indeed_scraper import scrape_indeed

@shared_task
def scrape_indeed_jobs():

    jobs = scrape_indeed()

    for job in jobs:
        Job.objects.create(
            title=job["title"],
            company=job["company"],
            location=job["location"],
            source=job["source"],
            url=job["url"]
        )

    return f"{len(jobs)} jobs saved"