from django.shortcuts import render, redirect
from django.contrib import messages
from port.models import Contact,Blogs,Internship
from django.core.mail import send_mail
from django.conf import settings
import requests

# Create your views here.

def home(request):
    return render(request, 'home.html')

def handleblog(request):
    posts=Blogs.objects.all()
    context={"posts":posts}
    return render(request, 'handleblog.html', context)

def about(request):
    return render(request, 'about.html')

def resume(request):
    return render(request, 'resume.html')

def thanks(request):
    return render(request, 'thanks.html')

def contact(request):
    if request.method == "POST":
        fname = request.POST.get('name')
        femail = request.user.email if request.user.is_authenticated else request.POST.get("email")
        fphoneno = request.POST.get('num')
        fcode = request.POST.get('country_code')
        fdesc = request.POST.get('desc')

        # ✅ Ensure all fields exist
        if not all([fname, femail, fphoneno, fdesc, fcode]):
            messages.error(request, "⚠️ Please fill in all fields.")
            return redirect('/contact')

        # ✅ Validate phone number
        if not fphoneno.isdigit():
            messages.error(request, "⚠️ Phone number must contain digits only.")
            return redirect('/contact')

        if len(fphoneno) > 15:
            messages.error(request, "⚠️ Phone number cannot exceed 15 digits.")
            return redirect('/contact')
        
        if not fphoneno.isdigit():
            messages.error(request, "⚠️ Phone number must contain digits only.")
            return redirect('/contact')

        # ✅ Save to DB
        query = Contact(name=fname, email=femail, phonenumber=fphoneno, description=fdesc)
        query.save()

        # ✅ Send email
        subject = f"New Contact Form Submission from {fname}"
        message = f"""
        Name: {fname}
        Email: {femail}
        Phone: {fphoneno}

        Message:
        {fdesc}
        """
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False
            )
        except Exception as e:
            messages.error(request, f"❌ Error sending email: {e}")

        # ✅ Send to Formspree
        try:
            payload = {"name": fname, "email": femail, "phone": fphoneno, "message": fdesc}
            response = requests.post(
                "https://formspree.io/f/xqadrgyy",
                data=payload,
                headers={"Accept": "application/json"}
            )
            if response.status_code in [200, 202]:
                messages.success(request, "✅ Your message has been sent successfully (via Formspree & Email).")
            else:
                messages.warning(request, f"⚠️ Message saved, but Formspree returned {response.status_code}.")
        except Exception as e:
            messages.error(request, f"❌ Saved & emailed, but failed to send to Formspree: {e}")

        return redirect('/contact')

    return render(request, 'contact.html')


def internshipdetails(request):

    if not request.user.is_authenticated:
        messages.warning(request, "please login to access this page")

        return redirect("/auth/login/")
    if request.method=="POST":

        fname=request.POST.get('name')
        femail=request.POST.get('email')
        fusn=request.POST.get('usn')
        fcollege=request.POST.get('cname')
        foffer=request.POST.get('offer')
        fstartdate=request.POST.get('startdate')
        fenddate=request.POST.get('enddate')
        fprojreport=request.POST.get('projectreport')
        
        # Converting to upper case upper()
        fname=fname.upper()
        fusn=fusn.upper()
        fcollege=fcollege.upper()
        foffer=foffer.upper()
        fprojreport=fprojreport.upper()

        # 
        check1=Internship.objects.filter(usn=fusn)
        check2=Internship.objects.filter(email=femail)

        if check1 or check2:

            messages.warning(request, "Your Details are Stored Aready")
            return redirect("/internshipdetails")

        query=Internship(fullname=fname, usn=fusn, email=femail, college=fcollege, 
                         offer_status=foffer, start_date=fstartdate, end_date=fenddate,
                         proj_report=fprojreport)
        query.save()

        messages.success(request, "Form is summitted, will be getting back to you soon!..")
        return redirect('/internshipdetails')



    return render(request, 'internship.html')


def cv_view(request):
    context = {
        "name": "Tolu Ayodele David",
        "roles": "Cybersecurity | SOC Analyst | Full-Stack Developer",
        "email": "tolexbrapline@yahoo.com",
        "phone": "+234 909 764 7130",
        "github": "https://github.com/TolexCozy/PRODUCTION_GET",
        "linkedin": "https://www.linkedin.com/in/tolu-ayodele-a5b893254/",
        "youtube": "https://www.youtube.com/@Tolexb-7",
        "professional_summary": "Multi-skilled technology professional with expertise in cybersecurity, SOC operations, and full-stack development...",
        "skills": {
            "Cybersecurity & SOC": [
                "Threat detection, incident response, vulnerability assessment",
                "SOC monitoring, SIEM tools (Splunk, ELK), IDS/IPS (Snort, Suricata)",
                "Penetration testing basics (Metasploit, Nmap, Burp Suite)",
                "Network security, malware analysis, secure coding"
            ],
            "Full-Stack Development": [
                "Frontend: HTML5, CSS3, JavaScript, React",
                "Backend: Python (Django), Node.js, REST APIs",
                "Databases: MySQL, MongoDB",
                "Version control & deployment: Git, Docker, CI/CD"
            ],
            "Tools & Platforms": [
                "Kali Linux, VirtualBox, VMware",
                "PowerShell, Bash scripting, Wireshark, Burp Suite, Hydra"
            ]
        },
        "experience": [
            {
                "title": "SOC Analyst Intern",
                "company": "BIZMARROW TECHNOLOGIES",
                "period": "MAR/2025 – OCT/2025",
                "duties": [
                    "Monitored security events and logs to detect suspicious activity using Splunk and Snort.",
                    "Assisted in incident response and documented security incidents.",
                    "Conducted vulnerability assessments and reported actionable findings."
                ]
            },
            {
                "title": "Full-Stack Developer (Freelance/Projects)",
                "company": "Self/Projects",
                "period": "JAN/2025 – OCT/2025",
                "duties": [
                    "Built Django-based e-commerce platforms with payment integrations.",
                    "Implemented secure authentication, product filtering, and search functionality.",
                    "Optimized UI using responsive design principles."
                ]
            }
        ],
        "projects": [
            {"name": "SOC Dashboard", "description": "Collected and analyzed logs, created Splunk dashboards for threat monitoring."},
            {"name": "Django E-commerce Site", "description": "Developed product listing, cart, payment integration, and AJAX search."},
            {"name": "Portfolio Website", "description": "Designed with Figma and built with HTML/CSS/JS showcasing full-stack projects."}
        ],
        "certifications": [
            "BIZMARROW TECHNOLOGIES",
            "CEH (Certified Ethical Hacker) (Completed)",
            "OSCP (Planned)",
        ],
        "additional_info": [
            "Languages: Python, JavaScript",
            "Soft Skills: Analytical thinking, problem-solving, collaboration, time management"
        ]
    }
    return render(request, "services.html", context)