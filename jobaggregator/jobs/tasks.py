from celery import shared_task
from jobs.scrapers.remoteok_scraper import scrape_remoteok
from .models import Job


@shared_task
def scrape_remoteok_jobs():

    jobs = scrape_remoteok()

    count = 0

    for job in jobs:

        Job.objects.update_or_create(
            url=job["url"],   # unique identifier
            defaults={
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "source": job["source"]
            }
        )

        count += 1

    return f"{count} jobs processed"