from django.conf.urls import url
from .views import *
from . import signals
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/movie/list')),
    url(r'^test/$', Test.as_view(), name="test"),
    url(r'^recommendation/demo/$', RecommendationDemo.as_view(), name="demo"),
    url(r'^profile/(?P<slug>[\w-]+)/$', ProfileView.as_view(), name="profile"),
    url(r'^register/$', RegistrationView.as_view(), name="register"),
    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    url(r'^genre/create/$', GenreCreateView.as_view(), name="genreCreate"),
    url(r'^genre/(?P<slug>[\w-]+)/update/$',
        GenreUpdateView.as_view(), name="genreUpdate"),
    url(r'^movie/create/$', MovieCreateView.as_view(), name="movieCreate"),
    url(r'^movie/(?P<slug>[\w-]+)/update/$',
        MovieUpdateView.as_view(), name="movieUpdate"),
    url(r'^movie/list/$', MovieListView.as_view(), name="movieList"),
    url(r'^movie/(?P<slug>[\w-]+)/$',
        MovieDetailView.as_view(), name='movieDetail'),
]
