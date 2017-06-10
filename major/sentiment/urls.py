from django.conf.urls import url

from .views import SentimentDemo

urlpatterns = [
    url(r'^$', SentimentDemo.as_view(), name='demo'),
]
