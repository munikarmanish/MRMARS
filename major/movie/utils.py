# from numpy import *
from scipy.optimize import minimize
from .models import Movie, Review
from django.contrib.auth.models import User
from django.conf import settings
import os
import logging

import pickle

import numpy as np

from movie.recommender import Recommender


def load_from_file(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


def save_to_file(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def numerical_grad(f, x, h=1e-8):
    grad = np.zeros_like(x)
    it = np.nditer(x, flags=['multi_index'])
    while not it.finished:
        index = it.multi_index
        original = x[index]
        x[index] = original + h
        f_high = f(x)
        x[index] = original - h
        f_low = f(x)
        x[index] = original
        grad[index] = (f_high - f_low) / (2 * h)
        it.iternext()
    return grad


def cf_cost(params, Y, R, num_features=Recommender.DEFAULT_NUM_FEATURES,
            reg=Recommender.DEFAULT_REGULARIZATION):
    # Unpack the parameters
    num_movies, num_users = Y.shape
    num_params = num_movies * num_features
    X = params[:num_params].reshape((num_movies, num_features))
    Theta = params[num_params:].reshape((num_users, num_features))

    J = 0
    X_grad = np.zeros_like(X)
    Theta_grad = np.zeros_like(Theta)

    # Cost
    J = 0.5 * (np.sum(((np.dot(X, Theta.T) - Y) * R)**2) +
               (reg * np.sum(Theta**2)) + (reg * np.sum(X**2)))

    # Gradients
    X_grad = np.dot(((np.dot(X, Theta.T) - Y) * R), Theta) + (reg * X)
    Theta_grad = np.dot(((np.dot(X, Theta.T) - Y) * R).T, X) + (reg * Theta)

    # serialize the paramters
    grad = np.concatenate((X_grad.flatten(), Theta_grad.flatten()))
    return (J, grad)


def normalize_ratings(Y, R):
    Y = Y.astype(float)
    num_movies, num_users = Y.shape
    Ymean = np.zeros(num_movies)
    Ynorm = np.zeros_like(Y)
    # loop for each movie
    for i in range(num_movies):
        idx = np.where(R[i, :] == 1)
        Ymean[i] = Y[i, idx].mean()
        Ynorm[i, idx] = Y[i, idx] - Ymean[i]
    return Ynorm, Ymean


def load_movie_list(filename=os.path.join(settings.BASE_DIR, "movie", "data", "movie_ids.txt")):
    with open(filename, 'r') as f:
        return [l.split(' ', 1)[1].strip() for l in f]


def demoRecommend(user_id=0):
    movies = load_movie_list()

    # Load the dataset
    y_file = os.path.join(settings.BASE_DIR, "movie", "data", "Y.bin")
    r_file = os.path.join(settings.BASE_DIR, "movie", "data", "R.bin")
    R = load_from_file(r_file)
    Y = load_from_file(y_file).astype(float)

    model_filename = os.path.join(settings.BASE_DIR, 'movie/data/recommender.pickle')
    if os.path.isfile(model_filename):
        model = Recommender.load(model_filename)
    else:
        my_ratings = np.zeros(len(movies))
        my_ratings[1 - 1] = 4
        my_ratings[98 - 1] = 2
        my_ratings[7 - 1] = 3
        my_ratings[12 - 1] = 5
        my_ratings[54 - 1] = 4
        my_ratings[64 - 1] = 5
        my_ratings[66 - 1] = 3
        my_ratings[69 - 1] = 5
        my_ratings[183 - 1] = 4
        my_ratings[226 - 1] = 5
        my_ratings[355 - 1] = 5
        Y = np.column_stack((my_ratings, Y))
        R = np.column_stack((my_ratings != 0, R))
        model = Recommender(Y=Y, R=R, reg=10, num_features=10)
        model.learn(maxiter=200, verbose=True, normalize=False, tol=1e-1)
        model.save(model_filename)

    rated_ids = [i for i in range(Y.shape[0]) if R[i, user_id] == 1]
    logging.info("USER {} HAS RATED:".format(user_id))
    rated = []
    for i in rated_ids:
        # logging.info("   RATED <{:.1f}> FOR '{}'".format(
        #     Y[i, user_id], movies[i]))
        rated.append("   Rated {:.1f} for '{}'".format(
            Y[i, user_id], movies[i]))
    recommendations = model.recommendations(user_id=user_id)
    logging.info("RECOMMENDATIONS FOR USER {}:".format(user_id))
    result = []

    max_rating = np.max([r for (i,r) in recommendations])
    if max_rating >= 5.0:
        recommendations = [(i, r*4.99/max_rating) for (i,r) in recommendations]
    for (i, rating) in recommendations:
        # logging.info("   <{:.1f}> {}".format(rating, movies[i]))
        result.append("   [{:.1f}] {}".format(rating * 4.99 / max_rating, movies[i]))

    return rated, result


def recommend(username):
    movies = Movie.objects.filter(deleted_at=None).order_by('title')
    users = User.objects.all().order_by('username')
    movieList, userList = [], []
    for movie in movies:
        movieList.append(movie.slug)

    for user in users:
        userList.append(user.username)
    print(movieList, userList)
    Y = np.zeros((len(movieList), len(userList)), dtype=float)
    R = np.zeros((len(movieList), len(userList)))
    reviews = Review.objects.filter(deleted_at=None)
    for review in reviews:
        x = movieList.index(review.movie.slug)
        y = userList.index(review.user.username)
        print(x, y)
        Y[x, y] = review.rating
        R[x, y] = 1
    print("end")
    print(Y, Y[1,1], type(Y[1,1]))
    model = Recommender(Y=Y, R=R, reg=10, num_features=10)
    model.learn(maxiter=200, verbose=True, normalize=False, tol=1e-1)
    user_id = 1
    rated_ids = [i for i in range(Y.shape[0]) if R[i, user_id] == 1]
    logging.info("USER {} HAS RATED:".format(user_id))
    rated = []
    for i in rated_ids:
        rated.append("   RATED <{:.1f}> FOR '{}'".format(
            Y[i, user_id], movieList[i]))
    recommendations = model.recommendations(user_id=user_id)
    logging.info("RECOMMENDATIONS:")
    result = []
    for (i, rating) in recommendations:
        result.append("   <{:.1f}> {}".format(rating, movieList[i]))

    return rated, result
    # return [],[]
