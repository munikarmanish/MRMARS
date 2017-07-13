# from numpy import *
from scipy.io import loadmat
from scipy.optimize import minimize
from json import loads
from .models import Movie, Data
from django.contrib.auth.models import User
from django.conf import settings
import os
from .tests import RecommenderTest


import os
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

# def cofiCostFunc(params, Y, R, num_users, num_movies, num_features, lambda_):
#     # COFICOSTFUNC Collaborative filtering cost function
#     #   J, grad = COFICOSTFUNC(params, Y, R, num_users, num_movies, num_features, lambda_)
#     #   returns the cost and gradient for the collaborative filtering problem.
#     #

#     # Unfold the U and W matrices from params
#     X = reshape(params[:num_movies * num_features],
#                 (num_movies, num_features), order='F')
#     Theta = reshape(params[num_movies * num_features:],
#                     (num_users, num_features), order='F')

#     # You need to return the following values correctly
#     J = 0
#     X_grad = zeros(shape(X))
#     Theta_grad = zeros(shape(Theta))

#     # ====================== YOUR CODE HERE ======================
#     # Instructions: Compute the cost function and gradient for collaborative
#     #               filtering. Concretely, you should first implement the cost
#     #               function (without regularization) and make sure it is
#     #               matches our costs. After that, you should implement the
#     #               gradient and use the checkCostFunction routine to check
#     #               that the gradient is correct. Finally, you should implement
#     #               regularization.
#     #
#     # Notes: X - num_movies  x num_features matrix of movie features
#     #        Theta - num_users  x num_features matrix of user features
#     #        Y - num_movies x num_users matrix of user ratings of movies
#     #        R - num_movies x num_users matrix, where R(i, j) = 1 if the
#     #            i-th movie was rated by the j-th user
#     #
#     # You should set the following variables correctly:
#     #
#     #        X_grad - num_movies x num_features matrix, containing the
#     #                 partial derivatives w.r.t. to each element of X
#     #        Theta_grad - num_users x num_features matrix, containing the
#     #                     partial derivatives w.r.t. to each element of Theta
#     #
#     J_temp = (dot(X, Theta.T) - Y)**2
#     J = (sum(J_temp[R == 1]) + lambda_ *
#          sum(sum(Theta**2)) + lambda_ * sum(sum(X**2))) / 2
#     # =============================================================

#     X_grad = dot(((dot(X, Theta.T) - Y) * R), Theta) + lambda_ * X
#     Theta_grad = dot(((dot(X, Theta.T) - Y) * R).T, X) + lambda_ * Theta

#     grad = hstack((X_grad.ravel('F'), Theta_grad.ravel('F')))
#     return J, grad


# def loadMovieList():
#     # GETMOVIELIST reads the fixed movie list in movie_ids.txt and returns a
#     # list of the titles
#     #   movieList = GETMOVIELIST() reads the fixed movie list in movie_ids.txt
#     #   and returns a list of the titles in movieList.
#     movieList = []
#     movies = Movie.objects.all()
#     for movie in movies:
#         movieList.append(movie.slug)
#     return movieList

# # returns list of all user in ascending order of name


# def loadUserList():
#     userList = []
#     users = User.objects.all().order_by('username')
#     for user in users:
#         userList.append(user.username)
#     return userList


# def loadDatas():
#     movieList = loadMovieList()
#     userList = loadUserList()
#     data = Data.objects.all().first()
#     data_dict = loads(data.data)
#     m, n = len(movieList), len(userList)
#     s = (m, n)
#     Y, R = zeros(s), zeros(s)
#     for user, value in data_dict.items():
#         for movie, rating in value.items():
#             x = movieList.index(movie)
#             y = userList.index(user)
#             Y[x, y] = rating
#             R[x, y] = 1
#     return movieList, userList, Y, R


# def normalizeRatings(Y, R):
#     # NORMALIZERATINGS Preprocess data by subtracting mean rating for every
#     # movie (every row)
#     #   Ynorm, Ymean = NORMALIZERATINGS(Y, R) normalized Y so that each movie
#     #   has a rating of 0 on average, and returns the mean rating in Ymean.
#     #

#     m, n = shape(Y)
#     Ymean = zeros(m)
#     Ynorm = zeros(shape(Y))
#     for i in range(m):
#         idx = where(R[i, :] == 1)
#         Ymean[i] = mean(Y[i, idx])
#         Ynorm[i, idx] = Y[i, idx] - Ymean[i]

#     return Ynorm, Ymean


# # ===== HELPERS =====


# def serialize(*args):
#     return hstack(a.ravel('F') for a in args)


def demoRecommend():
    # movieList = []

    # # Read the fixed movieulary list
    # with open(os.path.join(settings.BASE_DIR, "movie_ids.txt")) as fid:
    #     for line in fid:
    #         movieName = line.split(' ', 1)[1].strip()
    #         movieList.append(movieName)

    # #  Initialize my ratings
    # my_ratings = zeros(len(movieList))

    # # Check the file movie_idx.txt for id of each movie in our dataset
    # # For example, Toy Story (1995) has ID 1, so to rate it "4", you can set
    # my_ratings[1 - 1] = 4

    # # Or suppose did not enjoy Silence of the Lambs (1991), you can set
    # my_ratings[98 - 1] = 2

    # # We have selected a few movies we liked / did not like and the ratings we
    # # gave are as follows:
    # my_ratings[7 - 1] = 3
    # my_ratings[12 - 1] = 5
    # my_ratings[54 - 1] = 4
    # my_ratings[64 - 1] = 5
    # my_ratings[66 - 1] = 3
    # my_ratings[69 - 1] = 5
    # my_ratings[183 - 1] = 4
    # my_ratings[226 - 1] = 5
    # my_ratings[355 - 1] = 5
    # ex8_movies = loadmat(os.path.join(settings.BASE_DIR, "ex8_movies.mat"))
    # Y = ex8_movies['Y']
    # R = ex8_movies['R']

    # #  Normalize Ratings
    # Ynorm, Ymean = normalizeRatings(Y, R)

    # #  Useful Values
    # num_users = size(Y, 1)
    # num_movies = size(Y, 0)
    # num_features = 10

    # # Set Initial Parameters (Theta, X)
    # X = random.randn(num_movies, num_features)
    # Theta = random.randn(num_users, num_features)

    # initial_parameters = serialize(X, Theta)

    # # Set Regularization
    # lambda_ = 10
    # extra_args = (Ynorm, R, num_users, num_movies, num_features, lambda_)

    # res = minimize(cofiCostFunc, initial_parameters, extra_args, method='CG',
    #                jac=True, options={'maxiter': 100})
    # theta = res.x
    # cost = res.fun

    # # Unfold the returned theta back into U and W
    # X = reshape(theta[:num_movies * num_features],
    #             (num_movies, num_features), order='F')
    # Theta = reshape(theta[num_movies * num_features:],
    #                 (num_users, num_features), order='F')

    # p = dot(X, Theta.T)
    # nr = sum(R, 1)
    # my_predictions = p[:, 0]

    # ix = argsort(my_predictions)
    # print(ix)s
    # print(my_predictions[ix[-1]])
    # prediction = []
    # for j in ix[:-11:-1]:
    #     prediction.append('Predicting rating %.1f for movie %s' %
    #                       (my_predictions[j], movieList[j]))

    # original = []
    # for rating, name in zip(my_ratings, movieList):
    #     if rating > 0:
    #         original.append('Rated %d for %s' % (rating, name))
    original, prediction = RecommenderTest().test_recommendation()
    return original, prediction


def recommend(username):

    movieList, userList, Y, R = loadDatas()

    #  Normalize Ratings
    Ynorm, Ymean = normalizeRatings(Y, R)

    #  Useful Values
    num_users = size(Y, 1)
    num_movies = size(Y, 0)
    num_features = 10

    # Set Initial Parameters (Theta, X)
    X = random.randn(num_movies, num_features)
    Theta = random.randn(num_users, num_features)

    initial_parameters = serialize(X, Theta)

    # Set Regularization
    lambda_ = 10
    extra_args = (Y, R, num_users, num_movies, num_features, lambda_)
    res = minimize(cofiCostFunc, initial_parameters, extra_args, method='CG',
                   jac=True, options={'maxiter': 100})
    theta = res.x

    # Unfold the returned theta back into U and W
    X = reshape(theta[:num_movies * num_features],
                (num_movies, num_features), order='F')
    Theta = reshape(theta[num_movies * num_features:],
                    (num_users, num_features), order='F')

    p = dot(X, Theta.T)
    index = userList.index(username)
    my_predictions = p[:, index]

    ix = argsort(my_predictions)
    prediction = []
    prediction_dict = {}
    for j in ix[:-11:-1]:
        prediction.append('Predicting rating %.1f for movie %s' %
                          (my_predictions[j], movieList[j]))
        prediction_dict[movieList[j]] = my_predictions[j]

    return prediction, prediction_dict
