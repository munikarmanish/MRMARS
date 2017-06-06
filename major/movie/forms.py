from django import forms
from django.contrib.auth.models import User
from .models import *

from django.template.defaultfilters import slugify


class UserForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'required': 'true',
        'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'required': 'true',
        'placeholder': 'Re-type Password'}))

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {'class': 'form-control placeholder-no-fix'})

        self.fields["first_name"].widget.attrs.update(
            {'placeholder': 'First Name', 'required': 'true'})
        self.fields["last_name"].widget.attrs.update(
            {'placeholder': 'Last Name', 'required': 'true'})
        self.fields["username"].widget.attrs.update(
            {'placeholder': 'Username', 'required': 'true'})
        self.fields["email"].widget.attrs.update(
            {'placeholder': 'E-Mail', 'required': 'true'})

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError("You must confirm your password")
        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match")

        return password2


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-solid placeholder-no-fix',
        'required': 'true',
        'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-solid placeholder-no-fix',
        'required': 'true',
        'placeholder': 'Password', }))

    class Meta:
        fields = [
            "username",
            "password",
        ]


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = [
            "title",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {'class': 'form-control'})
        self.fields["title"].widget.attrs.update(
            {'placeholder': 'Genre Name', 'required': 'true'})

    def save(self, commit=True):
        instance = super(GenreForm, self).save(commit=False)
        instance.slug = slugify(self.cleaned_data.get('title'))
        if commit:
            instance.save()
        return instance


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie

        fields = [
            'title',
            'photo',
            'description',
            'released_date',
            'genre',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {'class': 'form-control'})
        self.fields["title"].widget.attrs.update(
            {'placeholder': 'Movie Name', 'required': 'true'})
        self.fields["photo"].widget.attrs.update(
            {'placeholder': 'Movie Photo', 'required': 'true'})
        self.fields["description"].widget.attrs.update(
            {'placeholder': 'Movie Description', 'required': 'true'})
        self.fields["released_date"].widget.attrs.update(
            {'placeholder': 'Movie Released Date(yy-mm-dd)', 'required': 'true', 'id':'datepicker'})
        self.fields["genre"].widget.attrs.update(
            {'placeholder': 'Movie Genre', 'required': 'true', 'id':'select2'})

    def save(self, commit=True):
        instance = super(MovieForm, self).save(commit=False)
        instance.slug = slugify(self.cleaned_data.get('title'))
        if commit:
            instance.save()
        return instance


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review

        fields = [
            'review',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {'class': 'form-control c-square'})
        self.fields["review"].widget.attrs.update(
            {'placeholder': 'Write Your Review', 'required': 'true'})
