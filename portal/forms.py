# portal/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import StudentProfile

class CampusRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    full_name = forms.CharField(max_length=150, required=True)
    contact_number = forms.CharField(max_length=15, required=True)
    hostel = forms.CharField(max_length=100, required=True)
    branch = forms.CharField(max_length=100, required=True)
    degree = forms.CharField(max_length=100, required=True)
    year_of_study = forms.IntegerField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@iiti.ac.in'):
            raise ValidationError("Access restricted! You must use an @iiti.ac.in email address.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Automatically create the linked profile
            StudentProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                contact_number=self.cleaned_data['contact_number'],
                hostel=self.cleaned_data['hostel'],
                branch=self.cleaned_data['branch'],
                degree=self.cleaned_data['degree'],
                year_of_study=self.cleaned_data['year_of_study']
            )
        return user