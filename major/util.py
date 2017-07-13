import os
import pickle

import numpy as np

from recommender import Recommender


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
        idx = np.where(R[i,:] == 1)
        Ymean[i] = Y[i, idx].mean()
        Ynorm[i,idx] = Y[i,idx] - Ymean[i]
    return Ynorm, Ymean


def load_movie_list(filename='data/movie_ids.txt'):
    with open(filename, 'r') as f:
        return [l.split(' ', 1)[1].strip() for l in f]
