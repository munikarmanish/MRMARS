import sys
from numpy import *
from scipy.io import loadmat
import random
from django.template.defaultfilters import slugify
from movie.models import Movie, Review

from django.contrib.auth import get_user_model

User = get_user_model()


ex8_movies = loadmat('ex8_movies.mat')
Y = ex8_movies['Y']
num_movies, num_user = shape(Y)
reviews = {
    1: ["I hate this movie!", "Worst movie of all time"],
    2: ["I didn't like this movie.", "The movie is very disturbing."],
    3: ["It is not bad at all.", "Exciting but not too much."],
    4: ["Good enough", "Awesome movie."],
    5: ["I loved everything about this movie!", "Best movie of all time."]
}

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
    for j in range(num_user):
        username = 'user' + str(j + 1)
        user = User.objects.get(username=username)
        if Y[i][j] != 0:
            try:
                print('Creating review {0}->{1} .'.format(username, title))
                review = Review()
                review.user = user
                review.movie = movie
                review.summary = random.choice(reviews[int(Y[i][j])])
                review.rating = Y[i][j]
                review.save()

                print(
                    'Review {0}->{1} successfully created.'.format(username, title))

            except:
                print ('There was a problem creating the review: {0}->{1}.  Error: {2}.'
                       .format(username, title, sys.exc_info()[1]))
