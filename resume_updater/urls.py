from django.urls import path
from .views import generate_resume, download_resume

urlpatterns = [
    path("", generate_resume, name="generate_resume"),
    path("download/<int:app_id>/", download_resume, name="download_resume"),
]
