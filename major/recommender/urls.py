from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^demo/$', RecommendationDemo.as_view(), name="demo"),
    url(r'^train/$', RecommendationTrain.as_view(), name="train"),
]
