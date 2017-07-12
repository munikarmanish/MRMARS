from datetime import date
from random import randint


movieList = []

with open('movie_ids.txt', encoding="latin1") as fid:
    for line in fid:
        print(line)
        movieName = line.split(' ', 1)[1].strip()
        movieList.append(movieName)
for i in range(len(movieList)):
    released_date = date(
        int(movieList[i][-5:-1]), randint(1, 12), randint(1, 28))
    print(i, type(released_date))

