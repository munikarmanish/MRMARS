import sys
from numpy import *
from scipy.io import loadmat
from django.template.defaultfilters import slugify
from movie.models import Movie


ex8_movies = loadmat('ex8_movies.mat')
Y = ex8_movies['Y']
num_movies, num_user = shape(Y)


movieList = []

# Read the fixed movieulary list
with open('movie_ids.txt', encoding="latin1") as fid:
    for line in fid:
        movieName = line.split(' ', 1)[1].strip()
        movieList.append(movieName)


for i in range(num_movies):
    title = movieList[i]
    slug = slugify(title) + '-' + str(i + 1)
    movie = Movie.objects.get(slug=slug)
    try:
        print('Creating total rating for  {0}.'.format(title))
        rating = true_divide(Y[i].sum(), (Y[i] != 0).sum())
        movie.rating = float(format(rating, '.1f'))
        movie.save()
        print('{0} rating successfully updated.'.format(title))

    except:
        print ('There was a problem updating the rating: {0}.  Error: {1}.'
               .format(title, sys.exc_info()[1]))
