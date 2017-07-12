import sys
import os
from movie.models import Movie
from datetime import date
from numpy import *
from scipy.io import loadmat
from random import randint
from django.template.defaultfilters import slugify
from django.core.files import File
from django.conf import settings


ex8_movies = loadmat('ex8_movies.mat')
Y = ex8_movies['Y']
num_movies, num_user = shape(Y)

movieList = []

# Read the fixed movieulary list
with open('movie_ids.txt', encoding="latin1") as fid:
    for line in fid:
        movieName = line.split(' ', 1)[1].strip()
        movieList.append(movieName)
description = """
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi magna neque, mollis id tellus ut, finibus rhoncus metus. Quisque id lectus auctor dolor pretium porttitor ut quis metus. Proin bibendum tincidunt scelerisque. Proin eu viverra mauris. Suspendisse potenti. Vestibulum fringilla lacus nec facilisis vulputate. Donec consectetur aliquam molestie. Curabitur fermentum enim ut euismod vestibulum. Ut aliquet scelerisque turpis, sit amet rutrum lacus iaculis vitae. Vestibulum dui metus, pulvinar porttitor neque eu, hendrerit gravida metus. Maecenas ultrices semper est ac blandit. Nunc mollis et massa malesuada rhoncus. Nunc pretium feugiat dolor eu lobortis. Donec tincidunt vulputate massa, ac tincidunt enim vehicula nec. Aenean ultricies est quis massa volutpat tincidunt. Etiam sollicitudin volutpat dui in facilisis.</p>

<p>Vestibulum ut risus in urna tincidunt vulputate. Donec molestie sodales sem, nec dictum nisi interdum nec. Nullam elementum vulputate est at aliquet. Ut dictum in enim vel pretium. Curabitur massa sapien, aliquet vel orci in, ornare lacinia turpis. Cras diam erat, consectetur vitae sollicitudin eu, tincidunt vel velit. Sed maximus eleifend turpis, id lacinia lacus vehicula at. Pellentesque id accumsan dolor, ac semper orci. Curabitur ut blandit dui, nec lacinia lacus. Nam eget est dui. Cras posuere sapien eget diam dictum, luctus vulputate risus accumsan. Ut consectetur libero suscipit, vehicula tellus sit amet, scelerisque turpis. Donec sed tristique arcu.</p>

<p>Phasellus eget convallis velit, vitae commodo dolor. Ut eget dolor lacinia, volutpat libero ac, commodo mauris. Nunc id nunc dui. Fusce sit amet laoreet velit, sit amet semper lectus. Sed eu rutrum nulla, at accumsan nibh. Sed in commodo nibh. In hendrerit in sem nec efficitur. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Ut eget efficitur elit. Vivamus fermentum mattis neque. Sed iaculis pulvinar suscipit. Maecenas sagittis erat ac dignissim fringilla.</p>

<p>Fusce scelerisque vehicula elit, imperdiet maximus ligula dignissim non. Curabitur molestie erat ornare ex vulputate varius. Duis suscipit enim libero, non ultricies nisi porttitor eget. Proin a lacus sit amet lacus tincidunt viverra ut non ipsum. Duis semper iaculis consectetur. Praesent vel massa lacus. Praesent in malesuada ligula, in ornare tortor. Nam nec neque ipsum. Quisque vel quam nulla. Nulla viverra posuere lacus, ut faucibus sapien ultricies ut. Nullam convallis ullamcorper turpis, vitae condimentum dui ultricies et. Quisque eu venenatis turpis, tempus accumsan enim. Cras aliquet justo ante, id tempor nisl aliquet vestibulum.</p>

<p>Praesent vestibulum metus eu egestas scelerisque. Nullam tempor lectus quis nunc cursus, nec porttitor augue luctus. Quisque placerat dolor eget nulla tempus dignissim. Suspendisse mollis iaculis sem a fringilla. Proin sapien erat, gravida sed est at, bibendum mollis leo. Aenean ullamcorper nisl nisi, in sollicitudin ipsum tempus sit amet. Phasellus convallis tellus pellentesque ex malesuada, sed pulvinar orci imperdiet. Pellentesque sit amet lorem nibh. Proin arcu odio, luctus at diam at, mattis eleifend eros. Nunc vulputate enim quis semper auctor. Duis urna lacus, molestie consectetur lacus non, vulputate mattis nisl. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Integer nec venenatis diam, sit amet rhoncus massa. Nunc a malesuada odio.
"""

for i in range(num_movies):
    title = movieList[i]
    released_date = date(
        int(movieList[i][-5:-1]), randint(1, 12), randint(1, 28))
    try:
        print('Creating movie {0}.'.format(title))
        movie = Movie()
        movie.title = title
        movie.slug = slugify(title) + '-' + str(i + 1)
        movie.released_date = released_date
        movie.description = description
        f = File(open(os.path.join(os.path.dirname(settings.BASE_DIR),
                                   "root", "media_cdn", "500x500.png"), 'rb'))
        movie.photo.save('{0}.png'.format(i + 1), f)
        movie.save()
        print('Movie {0} successfully created.'.format(title))

    except:
        print(released_date)
        print ('There was a problem creating the Movie: {0}.  Error: {1}.'
               .format(title, sys.exc_info()))
