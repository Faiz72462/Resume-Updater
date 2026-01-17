import os
import uuid
from django.shortcuts import render
from django.http import FileResponse
from django.core.files import File
from .forms import JobApplicationForm
from .resumeUpdater import genrator, parser, resume_updator, pdf_generotor, client
from django.shortcuts import redirect, get_object_or_404
from .models import JobApplication


from django.contrib.auth.decorators import login_required

@login_required
def generate_resume(request):
    apps = JobApplication.objects.all().order_by('-created_at')
    
    if request.method == "POST":
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            # Get data from form
            data = form.cleaned_data
            jd = data.get('jd', '')
            company = data.get('company', 'Unknown')
            country = data.get('country', 'India')
            job_portal = data.get('job_portal', 'Unknown')

            try:
                # 1. Generate content using Gemini
                response_text = genrator(client, jd)

                # 2. Parse the response
                summary, skills, experience, parsed_output = parser(response_text, country, company, job_portal)

                # Generate unique id for temp files
                unique_id = str(uuid.uuid4())
                docx_filename = f"temp_{unique_id}.docx"
                pdf_filename = f"temp_{unique_id}.pdf"

                try:
                    # 3. Update the DOCX
                    resume_updator(summary, skills, experience, country, docx_filename)

                    # 4. Convert to PDF
                    pdf_generotor(docx_filename, pdf_filename)

                    # 5. Save to Database
                    if os.path.exists(pdf_filename):
                        # Create DB Entry
                        job_app = JobApplication(
                            company=company,
                            country=country,
                            job_portal=job_portal,
                            resume_data=parsed_output
                        )
                        # Open the file and save it to the model
                        with open(pdf_filename, 'rb') as f:
                            job_app.resume_pdf.save(f"resume_{company}_{country}.pdf", File(f))
                        job_app.save()

                        return redirect(f'/?new_id={job_app.id}')
                    else:
                        return render(request, "home.html", {"form": form, "apps": apps, "error": "PDF file was not generated."})
                
                finally:
                    # Cleanup: Delete temporary files
                    if os.path.exists(docx_filename):
                        os.remove(docx_filename)
                    if os.path.exists(pdf_filename):
                        os.remove(pdf_filename)
            
            except Exception as e:
                return render(request, "home.html", {"form": form, "apps": apps, "error": f"An error occurred: {str(e)}"})

    else:
        form = JobApplicationForm()

    return render(request, "home.html", {"form": form, "apps": apps})

@login_required
def download_resume(request, app_id):
    app = get_object_or_404(JobApplication, id=app_id)
    return FileResponse(app.resume_pdf.open(), as_attachment=True, filename=f"Resume_{app.company}.pdf")
