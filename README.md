# Job Aggregator System

A scalable backend system that collects remote job listings from multiple sources and exposes them via a REST API.

The system uses **Django REST Framework, Celery, Redis, and PostgreSQL** to asynchronously scrape job data and serve it through a searchable API.

---

# Features

- Multi-source job scraping
- Asynchronous task processing with Celery
- Scheduled scraping using Celery Beat
- Job deduplication
- Search API
- Filtering by company and location
- Pagination
- Automatic cleanup of expired jobs

---

# Tech Stack

- Python
- Django
- Django REST Framework
- Celery
- Redis
- PostgreSQL

---

# Architecture
