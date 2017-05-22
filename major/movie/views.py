from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth import authenticate, login, logout
from .forms import *


# Create your views here.

class Test(TemplateView):
    template_name = "test.html"


class RegistrationView(View):
    def get(self, request):
        userForm = UserForm()
        context = {
            'userForm': userForm,
        }
        return render(request, 'registration.html', context)

    def post(self, request):
        userForm = UserForm(request.POST or None)
        if userForm.is_valid():
            user = userForm.save(commit=False)
            password = userForm.cleaned_data.get('password2')
            user.set_password(password)
            user.save()

            user = authenticate(username=user.username, password=password)
            messages.success(request, "Registration Successful")
            login(request, user)
            return redirect('account:test')

        context = {
            'userForm': userForm,
        }
        return render(request, 'registration.html', context)
