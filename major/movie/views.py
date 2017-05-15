from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.

class Test(TemplateView):
    template_name = "test.html"
