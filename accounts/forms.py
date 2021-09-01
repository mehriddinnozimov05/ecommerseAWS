from django import forms
from django.utils.html import format_html
from .models import Account, UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': "Enter Password",
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': "Enter Password again"
    }))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
        "type": "tel"
    }))

    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone_number", "email", "password"]
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean(self):
        clean_data = super(RegistrationForm, self).clean()
        password = clean_data.get("password")
        confirm_pasword = clean_data.get("confirm_password")
        
        if password != confirm_pasword:
            raise forms.ValidationError(
                "Password is not match."
            )
        if len(password) < 8 and len(password) != 0:
            raise forms.ValidationError(
                "Password too short."
            )

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone_number"]
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class ProfileForm(forms.ModelForm):
    picture = forms.ImageField(required=False, error_messages={"error":("Only Images!")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ["address_line1", "address_line2", "city", "state", "country", "picture"]
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['picture'].widget.attrs['class'] = 'form-control-file'