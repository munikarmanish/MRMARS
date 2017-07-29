import sys
from movie.models import Genre
from django.template.defaultfilters import slugify
genreList = []

with open('u.genre', encoding="latin1") as fid:
    for line in fid:
        genreName = line.split('|')[0].strip()
        genreList.append(genreName)
for i in range(len(genreList)):
    title = genreList[i]
    try:
        print('Creating genre {0}.'.format(title))
        genre = Genre()
        genre.title = title
        genre.slug = slugify(title)
        genre.save()
        print('Genre {0} successfully created.'.format(title))

    except:
        print ('There was a problem creating the Genre: {0}.  Error: {1}.'
               .format(title, sys.exc_info()))
