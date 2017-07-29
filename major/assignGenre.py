import sys
from movie.models import Genre, Movie
from django.template.defaultfilters import slugify

moviesGenreList = []
movieList = []
genreList = []
with open('u.item', encoding="latin1") as fid:
    for line in fid:
        list = []
        list.append(int(line.split('|')[5]))
        list.append(int(line.split('|')[6]))
        list.append(int(line.split('|')[7]))
        list.append(int(line.split('|')[8]))
        list.append(int(line.split('|')[9]))
        list.append(int(line.split('|')[10]))
        list.append(int(line.split('|')[11]))
        list.append(int(line.split('|')[12]))
        list.append(int(line.split('|')[13]))
        list.append(int(line.split('|')[14]))
        list.append(int(line.split('|')[15]))
        list.append(int(line.split('|')[16]))
        list.append(int(line.split('|')[17]))
        list.append(int(line.split('|')[18]))
        list.append(int(line.split('|')[19]))
        list.append(int(line.split('|')[20]))
        list.append(int(line.split('|')[21]))
        list.append(int(line.split('|')[22]))
        list.append(int(line.split('|')[23].rstrip()))
        moviesGenreList.append(list)

# Read the fixed movieulary list
with open('movie_ids.txt', encoding="latin1") as fid:
    for line in fid:
        movieName = line.split(' ', 1)[1].strip()
        movieList.append(movieName)

print(len(movieList), len(moviesGenreList))

with open('u.genre', encoding="latin1") as fid:
    for line in fid:
        genreName = line.split('|')[0].strip()
        genreList.append(genreName)


for i in range(len(movieList)):
    try:
        slug = slugify(movieList[i]) + '-' + str(i + 1)
        movie = Movie.objects.get(slug=slug)
        print('Adding genre to {}.'.format(movie.title))
        for j in range(len(moviesGenreList[i])):
            if moviesGenreList[i][j] == 1:
                genre = Genre.objects.get(title=genreList[j])
                movie.genre.add(genre)
        print('Adding genre to {} successful.'.format(movie.title))
    except:
        print ('There was a problem adding the Genre to movie: {0}.  Error: {1}.'
               .format(movie.title, sys.exc_info()))
