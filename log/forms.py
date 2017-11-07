import re
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
 
class signup_form(forms.Form):
    user_name=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'username','required':True}))
    user_email=forms.CharField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Your Email','required':True}))
    user_password=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'password','required':True}))
    user_confirmpassword=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password','required':True}))
   

class login_form(forms.Form):
    user_name=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'username','required':True}))
    user_password=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'password','required':True}))

class search_form(forms.Form):
	search_query=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter any keyword','required':True}))
