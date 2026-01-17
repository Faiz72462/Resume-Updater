from django.db import models

class JobApplication(models.Model):
    company = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    job_portal = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    resume_data = models.JSONField()
    resume_pdf = models.FileField(upload_to="resumes/")

    def __str__(self):
        return f"{self.company} ({self.country})"