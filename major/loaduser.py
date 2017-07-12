import sys
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from numpy import *
from scipy.io import loadmat

User = get_user_model()

ex8_movies = loadmat('ex8_movies.mat')
Y = ex8_movies['Y']
num_movies, num_user = shape(Y)

password = 'metalblOOd'

for i in range(num_user):
    username = 'user' + str(i + 1)
    first_name = 'User'
    last_name = str(i + 1)
    email = 'user_' + str(i + 1) + '@example.com'
    try:
        print('Creating user {0}.'.format(username))
        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.save()

        assert authenticate(username=username, password=password)
        print('User {0} successfully created.'.format(username))

    except:
        print ('There was a problem creating the user: {0}.  Error: {1}.'
               .format(username, sys.exc_info()[1]))
