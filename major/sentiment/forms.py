from django import forms


class SentimentDemoForm(forms.Form):
    review = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'required': 'true',
        'placeholder': 'Enter your review here...',
    }), label='Review')
