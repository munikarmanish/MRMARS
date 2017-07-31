from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, View, CreateView, ListView, DetailView, FormView, UpdateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.http import is_safe_url

from .forms import *
from .models import *
from recommender import utils as recommender
from sentiment import utils as sentiment


# Create your views here.


class LoginMixin(LoginRequiredMixin):
    login_url = '/login/'
    redirect_field_name = 'next'


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

            return redirect('movie:movieList')
        else:
            print(userForm.errors)

        context = {
            'userForm': userForm,
        }
        return render(request, 'registration.html', context)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            messages.warning(request, 'You are already registered.')
            return redirect('movie:movieList')
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        context = {
            'form': form,
        }
        return render(request, 'login.html', context)

    def post(self, request):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                messages.success(request, "Logged In Successfully")
                login(request, user)
                return redirect('movie:movieList')
        messages.warning(request, "Log In Failure")
        context = {
            'form': form,
        }
        return render(request, 'login.html', context)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            messages.warning(request, 'You are already logged in.')
            return redirect('movie:movieList')
        return super(LoginView, self).dispatch(request, *args, **kwargs)


class LogoutView(LoginMixin, View):

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            logout(request)
        messages.success(request, "Logged Out Successfully")
        return redirect('movie:login')


class ProfileView(LoginMixin, View):
    def get(self, request, *args, **kwargs):
        userSlug = kwargs['slug']
        user = User.objects.get(username=userSlug)
        reviews, predictions = recommender.recommend(user.pk)
        movies = Movie.objects.all().order_by('-rating')[:12]
        voteUp = 0
        voteDown = 0
        for review in reviews:
            votes = Vote.objects.filter(review=review)
            downVotes = votes.filter(up=False)
            upVotes = votes.filter(up=True)
            voteUp += len(upVotes)
            voteDown += len(downVotes)

        reputation = voteUp - voteDown

        context = {
            'reputation': reputation,
            'user': user,
            'reviews': reviews,
            'predictions': predictions,
            'movies': movies,
        }
        return render(request, 'profile.html', context)


class GenreCreateView(CreateView):
    model = Genre
    form_class = GenreForm
    template_name = 'genreCreate.html'
    success_url = reverse_lazy("movie:test")


class GenreUpdateView(UpdateView):
    model = Genre
    form_class = GenreForm
    template_name = 'genreUpdate.html'
    success_url = reverse_lazy("movie:test")


class MovieCreateView(CreateView):
    model = Movie
    form_class = MovieForm
    template_name = 'movieCreate.html'
    success_url = reverse_lazy("movie:test")

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.slug = slugify(form.cleaned_data.get('title'))
        instance.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return redirect(reverse_lazy("movie:movieCreate"))


class MovieUpdateView(UpdateView):
    model = Movie
    form_class = MovieForm
    template_name = 'movieUpdate.html'
    success_url = reverse_lazy("movie:test")

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.slug = slugify(form.cleaned_data.get('title'))
        instance.save()
        return super().form_valid(form)


class MovieListView(ListView):
    model = Movie
    template_name = 'movieList.html'
    context_object_name = 'movies'
    paginate_by = 16

    def get_queryset(self):
        movies = Movie.objects.filter(deleted_at=None)
        query = self.request.GET.get("q")
        if query:
            movies = movies.filter(
                Q(title__icontains=query) |
                Q(genre__title__icontains=query)
            ).distinct()
        return movies


class MovieDetailView(FormView):
    form_class = ReviewForm
    template_name = 'movieDetail.html'

    def dispatch(self, request, *args, **kwargs):
        self.movie_slug = kwargs['slug']
        self.movie = Movie.objects.get(slug=self.movie_slug)
        return super(MovieDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MovieDetailView, self).get_context_data(**kwargs)

        context['movie'] = self.movie
        context['reviews'] = Review.objects.filter(movie=self.movie)
        similarMoviesList = []
        for genre in self.movie.genre.all():
            movies = Movie.objects.filter(genre=genre)
            for movie in movies:
                if movie.rating == 5:
                    similarMoviesList.append(movie)
        similarMoviesId = [movie.id for movie in similarMoviesList]
        similarMovies = Movie.objects.filter(
            id__in=similarMoviesId).order_by('-rating')[:4]
        context['similarMovies'] = similarMovies
        return context

    def form_valid(self, form):
        review = Review()
        if Review.objects.filter(user=self.request.user, movie=self.movie):
            messages.warning(self.request, 'You have already reviewed.')
            return HttpResponseRedirect(self.movie.get_absolute_url())
        review.user = self.request.user
        review.movie = self.movie
        review.review = form.cleaned_data.get('review')
        review.summary = form.cleaned_data.get('summary')
        review.rating = sentiment.rating(review.summary)
        review.save()
        return HttpResponseRedirect(self.movie.get_absolute_url())


class VoteUpView(LoginMixin, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        username = kwargs['username']
        slug = kwargs['slug']
        review = Review.objects.get(pk=pk)
        user = User.objects.get(username=username)
        movie = Movie.objects.get(slug=slug)
        voteObj = Vote.objects.filter(user=user, review=review)
        if user == review.user:
            messages.warning(self.request, 'You cannot vote your own review.')
            return HttpResponseRedirect(movie.get_absolute_url())
        if len(voteObj) == 1:
            if len(voteObj.filter(up=True)) == 1:
                print('hello')
                messages.warning(self.request, 'You have already voted up.')
                return HttpResponseRedirect(movie.get_absolute_url())
            else:
                vote = voteObj.first()
                vote.up = True
                vote.save()
                review.vote_count += 1
                review.save()
                return HttpResponseRedirect(movie.get_absolute_url())
        else:

            vote = Vote()
            vote.user = user
            vote.review = review
            vote.up = True
            vote.save()
            review.vote_count += 1
            review.save()
            return HttpResponseRedirect(movie.get_absolute_url())


class VoteDownView(LoginMixin, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        username = kwargs['username']
        slug = kwargs['slug']
        review = Review.objects.get(pk=pk)
        user = User.objects.get(username=username)
        movie = Movie.objects.get(slug=slug)
        voteObj = Vote.objects.filter(user=user, review=review)
        if user == review.user:
            messages.warning(self.request, 'You cannot vote your own review.')
            return HttpResponseRedirect(movie.get_absolute_url())
        if len(voteObj) == 1:
            if len(voteObj.filter(up=False)) == 1:
                print('hello')
                messages.warning(self.request, 'You have already voted down.')
                return HttpResponseRedirect(movie.get_absolute_url())
            else:
                vote = voteObj.first()
                vote.up = False
                vote.save()
                review.vote_count -= 1
                review.save()
                return HttpResponseRedirect(movie.get_absolute_url())
        else:

            vote = Vote()
            vote.user = user
            vote.review = review
            vote.up = False
            vote.save()
            review.vote_count -= 1
            review.save()
            return HttpResponseRedirect(movie.get_absolute_url())
