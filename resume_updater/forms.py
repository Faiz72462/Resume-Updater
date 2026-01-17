from django import forms

class JobApplicationForm(forms.Form):
    company = forms.CharField()
    country = forms.CharField()
    job_portal = forms.CharField()
    jd = forms.CharField(widget=forms.Textarea(attrs={"rows": 12}))
