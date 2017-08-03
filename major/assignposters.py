import random

from movie.models import Movie

NUM_POSTERS = 30

count = 0
for movie in Movie.objects.all():
    count += 1
    movie.photo = 'movie-poster-{}.jpg'.format(random.randint(1, NUM_POSTERS))
    movie.save()
    print("{:4.0f}.  {}".format(count, movie.title))
