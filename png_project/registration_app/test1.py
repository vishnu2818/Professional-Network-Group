from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Company
from .serializers import CompanySerializer
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib import messages
from .models import Company
from django.contrib.auth.models import User
from django.shortcuts import render
from .models import Company

class CompanyRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response({"message": "Registration submitted successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminApprovalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
            if request.data.get("status") in ["approved", "rejected"]:
                company.status = request.data["status"]
                company.save()
                return Response({"message": f"Company status updated to {company.status}."}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)
        except Company.DoesNotExist:
            return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)


from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm

def registration_form(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)  # Don't save immediately
            company.created_by = request.user  # Assign the logged-in user to 'created_by'
            company.save()  # Save the company instance

            messages.success(request, "Company registered successfully!")
            return redirect('login')  # Redirect after successful registration
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
            company = Company.objects.get(email=email)

            if password == company.password:
                # Create or get the User object associated with the company email
                user, created = User.objects.get_or_create(username=email, defaults={'email': email})
                auth_login(request, user)  # Log the user in

                return redirect('landing')  # Redirect to landing page after successful login
            else:
                messages.error(request, "Invalid email or password.")  # Password mismatch
        except Company.DoesNotExist:
            messages.error(request, "No company found with that email.")  # No company found with the given email

    return render(request, 'login.html')



def landing_page(request):
    company = None
    companies = Company.objects.all()  # Fetch all companies
    print("All Companies:")
    for comp in companies:
        print(f"Company Name: {comp.name}")
        print(f"Email: {comp.email}")
        print(f"Status: {comp.status}")
        print(f"Description: {comp.description}")
        print(f"Logo: {comp.logo.url if comp.logo else 'No logo'}")
        print(f"Banner: {comp.banner.url if comp.banner else 'No banner'}")
        print(f"Created By: {comp.created_by.email}")
        print("-" * 30)  # Separator for readability

    if request.user.is_authenticated:
        print(f"Logged-in User: {request.user.email}")
        try:
            # Fetch the company where the company email matches the logged-in user's email
            company = Company.objects.get(email=request.user.email)
            print(f"Company Name: {company.name}")
            print(f"Email: {company.email}")
            print(f"Status: {company.status}")
            print(f"Description: {company.description}")
            print(f"Logo: {company.logo.url if company.logo else 'No logo'}")
            print(f"Banner: {company.banner.url if company.banner else 'No banner'}")
            print(f"Created By: {company.created_by.email}")
        except Company.DoesNotExist:
            print("No company found for the logged-in user.")

    return render(request, 'landing.html', {'company': company})



def partners(request):
    # Query all companies
    companies = Company.objects.all()
    print(companies)
    return render(request, 'partners.html', {'companies': companies})