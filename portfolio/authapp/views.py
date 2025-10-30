from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.models import User
import random
from .models import EmailVerification


def signup(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('pass1')
        confirm_password = request.POST.get('pass2')

        # Validate inputs
        if not name:
            messages.error(request, "Name cannot be empty")
            return redirect('/auth/signup/')

        if password != confirm_password:
            messages.warning(request, "Passwords do not match")
            return redirect('/auth/signup/')

        # 🧩 Check for existing user
        user = User.objects.filter(username=email).first()

        if user:
            if user.is_active:
                messages.warning(request, "Email is already verified and registered.")
                return redirect('/auth/signup/')
            else:
                # User exists but not verified → resend PIN
                record = EmailVerification.objects.filter(user=user).first()
                if record:
                    record.delete()

                pin = random.randint(100000, 999999)
                EmailVerification.objects.create(
                    user=user,
                    pin=pin,
                    expires_at=timezone.now() + timedelta(minutes=10)
                )

                send_mail(
                    subject="Your Verification PIN",
                    message=f"Your verification code is: {pin}\n\nIt expires in 10 minutes.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )

                messages.info(request, "A new verification PIN has been sent to your email.")
                return redirect(f'/auth/verify/?email={email}')

        # 🧩 Create new inactive user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.last_name = last_name
        user.is_active = False
        user.save()

        # Generate and save PIN
        pin = random.randint(100000, 999999)
        EmailVerification.objects.create(
            user=user,
            pin=pin,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        # Send email
        send_mail(
            subject="Your Verification PIN",
            message=f"Your verification code is: {pin}\n\nIt expires in 10 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.info(request, "A verification PIN has been sent to your email.")
        return redirect(f'/auth/verify/?email={email}')

    return render(request, 'signup.html')



def verify_email(request):
    email = request.GET.get('email')
    sent_pin_message = None

    if not email:
        messages.error(request, "Verification link invalid or missing email.")
        return redirect('/auth/signup/')

    user = User.objects.filter(email=email).first()

    # 🧩 Handle case: email not found or already verified
    if not user:
        messages.error(request, "Email not found. Please sign up again.")
        return redirect('/auth/signup/')
    if user.is_active:
        messages.info(request, "Email already verified. Please log in.")
        return redirect('/auth/login/')

    # 🧩 Handle POST: user submitting PIN
    if request.method == "POST":
        pin = request.POST.get('pin', '').strip()

        record = EmailVerification.objects.filter(user=user).first()
        if not record:
            messages.error(request, "No active verification record found.")
            return redirect(f'/auth/verify/?email={email}')

        # Expired PIN check
        if timezone.now() > record.expires_at:
            record.delete()
            messages.error(request, "PIN expired. Please request a new one.")
            return redirect(f'/auth/resend/?email={email}')

        # PIN match check
        if record.pin == pin:
            user.is_active = True
            user.save()
            record.delete()
            messages.success(request, "✅ Email verified successfully! You can now log in.")
            return redirect('/auth/login/')
        else:
            messages.error(request, "Incorrect PIN. Please try again.")
            return redirect(f'/auth/verify/?email={email}')

    else:
        # When page first loads — show friendly info message
        sent_pin_message = f"A verification PIN has been sent to {email}. Please check your inbox (and spam folder)."

    # Render verification page
    return render(request, 'verify.html', {
        'email': email,
        'sent_pin_message': sent_pin_message
    })




def resend_pin(request):
    email = request.GET.get('email')

    # 🧩 1. Find user by email (case-insensitive)
    user = User.objects.filter(email__iexact=email).first()

    if not user:
        messages.error(request, "Email not found.")
        return redirect('/auth/signup/')

    # 🧩 2. Check if user already verified
    if user.is_active:
        messages.info(request, "This email is already verified. Please log in instead.")
        return redirect('/auth/login/')

    # 🧩 3. Delete old verification records (if any)
    EmailVerification.objects.filter(user=user).delete()

    # 🧩 4. Generate a new 6-digit PIN
    pin = random.randint(100000, 999999)

    # 🧩 5. Create a new verification entry
    EmailVerification.objects.create(
        user=user,
        pin=pin,
        expires_at=timezone.now() + timedelta(minutes=10)
    )

    # 🧩 6. Prepare the email content
    subject = "Your Email Verification Code"
    text_message = f"""
Hi {user.first_name or user.username},

Your verification PIN for login is {pin}.

Enter this 6-digit code on the verification page to complete your signup.
This PIN expires in 10 minutes.

Thank you,
Your Security Team
    """.strip()

    # Optional — HTML version (for styled email)
    html_message = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
      <div style="max-width: 500px; background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h2 style="color: #1a73e8;">Email Verification</h2>
        <p>Hi <strong>{user.first_name or user.username}</strong>,</p>
        <p>Your verification code is:</p>
        <h1 style="color: #1a73e8; letter-spacing: 2px;">{pin}</h1>
        <p>This code will expire in <strong>10 minutes</strong>.</p>
        <p style="margin-top: 20px;">Thanks,<br><strong>Your Security Team</strong></p>
      </div>
    </div>
    """

    # 🧩 7. Send the email (text + HTML)
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[email],
    )
    email_message.attach_alternative(html_message, "text/html")
    email_message.send(fail_silently=False)

    # 🧩 8. Feedback to user
    messages.success(request, "A new verification PIN has been sent to your email.")
    return redirect(f'/auth/verify/?email={email}')




def handlelogin(request):
    if request.method == "POST":
        email = request.POST.get('email').strip().lower()
        password = request.POST.get('pass1')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful")
            return redirect("/")
        else:
            messages.error(request, "Invalid Credentials")

    return render(request, 'login.html')


def handlelogout(request):
    logout(request)
    messages.success(request, 'Logout Successful')
    return redirect('/auth/login/')