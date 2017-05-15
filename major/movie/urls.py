from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^test/$', Test.as_view(), name="test"),
]
