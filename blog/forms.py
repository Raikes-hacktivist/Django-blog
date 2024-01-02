from django import forms
from .models import Post, Comment
from captcha.fields import ReCaptchaField
from django.core import validators

        
class PostForm(forms.ModelForm):
    title = forms.CharField(max_length=128)
    body = forms.CharField(max_length=245, label="Item Description.")

    class Meta:
        model = Post
        fields = ('title', 'body',  )

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=30)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body',)
        
    

class ContactForm(forms.Form):
    name = forms.CharField(required=True, max_length=250)
    company = forms.CharField(max_length=250,required=False)
    email = forms.EmailField(required=True)
    message = forms.CharField(required=True, widget=forms.Textarea)

class SubscriberForm(forms.Form):
    email = forms.EmailField(max_length=100,
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    
    

