from .forms import RegistrationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.hashers import make_password
from .models import Company
from .forms import CompanyForm
from django.contrib.auth import authenticate, login
from .models import NewsUpload
from .forms import NewsForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
from .forms import EventForm
from django.contrib import messages
from django.db import IntegrityError

def index(request):  # Latest news first
    companies = Company.objects.filter(status='approved')

    # Query all news articles ordered by publication date (most recent first)
    news_articles = NewsUpload.objects.order_by('-publication_date')

    # Query all events
    events = Event.objects.all()

    # Render the template and pass the context
    return render(request, 'index.html', {
        'companies': companies,
        'news_articles': news_articles[:11],  # Pass all news articles here
        'events': events[:11], })


# def registration_form(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST, request.FILES)
#         if form.is_valid():
#             company = form.save(commit=False)  # Don't save immediately
#             # company.created_by = request.user  # Assign the logged-in user to 'created_by'
#             company.save()  # Save the company instance
#             messages.success(request, "Company registered successfully!")
#             return redirect('index')  # Redirect after successful registration
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = RegistrationForm()
#
#     return render(request, 'register.html', {'form': form})

# def registration_form(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST, request.FILES)
#         if form.is_valid():
#             company = form.save(commit=False)  # Don't save immediately
#             company.created_by = request.user  # Assign the logged-in user to 'created_by'
#
#             # Process the bulleted_list field
#             # bulleted_list = form.cleaned_data.get('bulleted_list', '')
#             # processed_bullets = '\n'.join([line if line.startswith('*') else f'* {line}' for line in bulleted_list.splitlines() if line.strip()])
#             # company.bulleted_list = processed_bullets
#
#             company.save()  # Save the company instance
#
#             messages.success(request, "Company registered successfully!")
#             return redirect('login')  # Redirect after successful registration
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = RegistrationForm()
#
#     return render(request, 'register.html', {'form': form})

def registration_form(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)  # Don't save immediately

            # Ensure the user is authenticated before assigning
            if request.user.is_authenticated:
                company.created_by = request.user  # Assign the logged-in user to 'created_by'
            else:
                # If not authenticated, you can either redirect or set to a default user
                messages.error(request, "You must be logged in to register a company.")
                return redirect('login')  # Redirect to login page

            company.save()  # Save the company instance

            messages.success(request, "Company registered successfully!")
            return redirect('index')  # Redirect after successful registration
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Fetch the company using the provided email
            company = Company.objects.get(email=email)

            # Check if the company's status is 'approved'
            if company.status != 'approved':
                messages.error(request, "Your account is not approved yet.")
                return render(request, 'login.html')

            # Use check_password to validate the entered password against the hashed password
            if check_password(password, company.password):
                # Ensure the User object exists
                user, created = User.objects.get_or_create(
                    username=email,
                    defaults={'email': email},
                )

                # Log the user in
                auth_login(request, user)

                return redirect('landing')  # Redirect to landing page on success
            else:
                messages.error(request, "Invalid email or password.")  # Password mismatch
        except Company.DoesNotExist:
            messages.error(request, "No company found with that email.")  # Company not found

    return render(request, 'login.html')




def company_landing_page(request, company_id):
    try:
        # Fetch the company by ID
        company = Company.objects.get(id=company_id, status='approved')
        print(f"Company Landing Page for: {company.banner_content}")
        print(f"Email: {company.email}")
        print(f"Status: {company.status}")
        print(f"Description: {company.description}")
        print(f"Logo: {company.logo.url if company.logo else 'No logo'}")
        print(f"Banner: {company.banner.url if company.banner else 'No banner'}")
    except Company.DoesNotExist:
        messages.error(request, "Company not found.")
        return redirect('partners')  # Redirect back to the partners page if the company doesn't exist

    return render(request, 'landing.html', {'company': company})



def reset_password(request, uidb64, token):
    try:
        # Decode user id from the URL
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            # Process the password reset form
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                # Save the new password to the User model
                form.save()

                # Also update the password in the Company model
                # Find the corresponding Company record
                try:
                    company = Company.objects.get(created_by=user)
                    company.password = make_password(form.cleaned_data['new_password1'])
                    company.save()
                    messages.success(request, "Your password has been reset successfully.")
                except Company.DoesNotExist:
                    messages.error(request, "Company associated with this user not found.")

                return redirect('login')
        else:
            form = SetPasswordForm(user)

        return render(request, 'reset_password.html', {'form': form})
    else:
        messages.error(request, "The reset link is invalid or expired.")
        return redirect('forgot_password')



def forgot_password(request):
    if request.method == 'POST':
        # Step 1: Get email from the form
        email = request.POST.get('email')
        print(f"POST request received. Email entered: {email}")

        # Check if email is empty
        if not email:
            print("No email provided.")
            messages.error(request, "Please provide an email address.")
            return redirect('forgot_password')  # Redirect back to the form

        try:
            # Step 2: Fetch the company using the provided email
            company = Company.objects.get(email=email)
            print(f"Company found. Company email: {company.email}")

            # Step 3: Compare emails
            print(f"User typed email: {email}")
            print(f"Company stored email: {company.email}")

            if email == company.email:
                print("Emails match!")  # This should show in the logs if emails match

                # Step 4: Check if new password is being submitted
                if 'new_password' in request.POST:
                    new_password = request.POST.get('new_password')
                    print(f"New password received: {new_password}")

                    # Step 5: Hash the new password and save it
                    company.password = make_password(new_password)
                    company.save()
                    print("Password updated successfully.")

                    messages.success(request, "Password updated successfully.")
                    return redirect('login')  # Redirect to login page after updating password

                # Step 6: Render the form to enter new password
                print("Rendering new password form.")
                return render(request, 'forgot_password.html', {'email': email, 'step': 'new_password'})

            else:
                print("Emails do not match!")  # Debugging mismatch (though unlikely)

        except Company.DoesNotExist:
            print(f"No company found with email: {email}")
            messages.error(request, "No company found with that email.")
            return redirect('forgot_password')

    # If the method is GET or the user is still on the first step, show the email form
    print("GET request or initial POST request, rendering email input form.")
    return render(request, 'forgot_password.html')



def superuser_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            messages.success(request, "Login successful!")
            # return redirect('company_list')
            return redirect('admin_page')  # Redirect to company list
        else:
            messages.error(request, "Invalid credentials or not a superuser.")
    return render(request, 'admin_login.html')  # Custom login template


def is_superuser(user):
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def company_list(request):
    companies = Company.objects.all()
    return render(request, 'company_list.html', {'companies': companies})


@login_required
@user_passes_test(is_superuser)
def company_create(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Company created successfully!")
            return redirect('company_list')
    else:
        form = CompanyForm()
    return render(request, 'add_new_company.html', {'form': form})



@login_required
@user_passes_test(is_superuser)
def company_update(request, pk):
    company = get_object_or_404(Company, pk=pk)

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)

        if form.is_valid():
            form.save()
            messages.success(request, "Company updated successfully!")
            return redirect('company_list')  # Redirect after successful update
        else:
            messages.error(request, "There was an error with the form. Please check your input.")

    else:
        form = CompanyForm(instance=company)

    return render(request, 'company_update.html', {'form': form, 'company': company})


@login_required
@user_passes_test(is_superuser)
def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.delete()
        messages.success(request, "Company deleted successfully!")
        return redirect('company_list')
    return render(request, 'company_confirm_delete.html', {'company': company})



def news_list(request):
    news_articles = NewsUpload.objects.order_by('-publication_date')  # Latest news first
    return render(request, 'news_list.html', {'news_articles': news_articles})


def create_news(request):
    if request.method == "POST":
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('news_list')
    else:
        form = NewsForm()
    return render(request, 'news_create.html', {'form': form})


def news_page(request, news_id):
    try:
        news = NewsUpload.objects.get(id=news_id)
    except NewsUpload.DoesNotExist:
        messages.error(request, "News not found.")
        return redirect('news_list')  # Redirect back to the  page if the company doesn't exist

    return render(request, 'news_content.html', {'news': news})


# method for event creation
def event_list(request):
    events = Event.objects.order_by('-date')  # Latest Event first
    return render(request, 'event_list.html', {'events': events})


def create_event(request):
    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES)
        if event_form.is_valid():
            event_form.save()
            return redirect('event_list')
    else:
        event_form = EventForm()
    return render(request, 'event_create.html', {'event_form': event_form})


def event_page(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        messages.error(request, "Event not found.")
        return redirect('event_list')  # Redirect back to the partners page if the company doesn't exist

    return render(request, 'news_content.html', {'event': event})


# Create
# def news_create(request):
#     if request.method == 'POST':
#         form = NewsForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "News article created successfully.")
#             return redirect('news_list')
#     else:
#         form = NewsForm()
#     return render(request, 'news_create.html', {'form': form})



# Update
def news_update(request, news_id):
    news = get_object_or_404(NewsUpload, id=news_id)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, "News article updated successfully.")
            return redirect('news_list')
    else:
        form = NewsForm(instance=news)
    return render(request, 'news_update.html', {'form': form, 'news': news})


# Delete
def news_delete(request, news_id):
    news = get_object_or_404(NewsUpload, id=news_id)
    if request.method == 'POST':
        news.delete()
        messages.success(request, "News article deleted successfully.")
        return redirect('news_list')
    return render(request, 'news_delete.html', {'news': news})


# View to display all events
def event_list(request):
    events = Event.objects.all()
    return render(request, 'event_list.html', {'events': events})


# View to display a single event's details
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_detail.html', {'event': event})


# View to update an event
def event_update(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'event_update.html', {'form': form})


# View to delete an event
def event_delete(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('event_list')
    return render(request, 'event_confirm_delete.html', {'event': event})

def admin_page(request):
    return render(request, 'admin_page.html')


def about(request):
    return render(request, 'about.html')


def landing(request):
    company = None
    if request.user.is_authenticated:
        try:
            # Fetch the company for the logged-in user with status 'approved'
            company = Company.objects.filter(email=request.user.email, status='approved').first()
            if not company:
                print("No approved company found for this user.")
        except Company.DoesNotExist:
            print("No company found for this user.")
    return render(request, 'landing.html', {'company': company})

def events(request):
    # events = Event.objects.order_by('-date')  # Latest Event first
    query = request.GET.get('search', '').strip()
    cleaned_query = re.sub(r'[^\w\s]', '', query)

    if query:
        events = Event.objects.filter(Q(name__icontains=cleaned_query) |
                                      Q(location__icontains=cleaned_query))
    else:
        events = Event.objects.order_by('-date')

    # Output companies for debugging
    for event in events:
        print(f"Company Name: {event.name}, Services: {event.location}")
    return render(request, 'events_news.html', {'events': events})

def news_new(request):
    query = request.GET.get('search', '').strip()
    cleaned_query = re.sub(r'[^\w\s]', '', query)

    if query:
        news_articles = NewsUpload.objects.filter(Q(title__icontains=cleaned_query) |
                                      Q(author__icontains=cleaned_query))
    else:
        news_articles = NewsUpload.objects.order_by('-publication_date')

    # Output companies for debugging
    for news in news_articles:
        print(f"Company Name: {news.title}, Services: {news.author}")

    return render(request, 'events_news.html', {'news_articles': news_articles})

# def partners(request):
#     companies = Company.objects.filter(status='approved')
#     return render(request, 'events_news.html', {'companies': companies})

from django.db.models import Q
import re

def partners(request):
    query = request.GET.get('search', '').strip()
    cleaned_query = re.sub(r'[^\w\s]', '', query)
    if query:
        companies = Company.objects.filter(
            Q(status='approved') &
            (Q(name__icontains=cleaned_query) | Q(services__icontains=cleaned_query)))
    else:
        companies = Company.objects.filter(status='approved')

    # Output companies for debugging
    for company in companies:
        print(f"Company Name: {company.name}, Services: {company.services}")

    return render(request, 'events_news.html', {'companies': companies, 'query': query})
