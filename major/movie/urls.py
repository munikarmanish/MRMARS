from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^test/$', Test.as_view(), name="test"),
    url(r'^register/$', RegistrationView.as_view(), name="register"),
    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    url(r'^genre/create/$', GenreCreateView.as_view(), name="genreCreate"),
]
