from django.db import models

class Job(models.Model):

    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    source = models.CharField(max_length=100)
    url = models.URLField(unique=True)

    # 🔥 NEW FIELDS
    description = models.TextField(null=True, blank=True)
    skills = models.JSONField(default=list)
    experience_level = models.CharField(max_length=100, null=True, blank=True)

    # Embedding (for RAG later)
    embedding = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title