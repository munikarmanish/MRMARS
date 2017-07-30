"""
This module implements a class that represents the low-rank matrix
factorization-based collaborative-filtering recommender algorithm.
"""

import logging
import sys

import numpy as np
from scipy.optimize import minimize


class Recommender:

    # Some default parameters
    DEFAULT_NUM_FEATURES = 10
    DEFAULT_REGULARIZATION = 1
    DEFAULT_MAX_ITER = 1000

    def __init__(self, num_features=DEFAULT_NUM_FEATURES, normalized=False,
                 reg=DEFAULT_REGULARIZATION, Y=None, R=None):
        """
        Initialize the recommender algorithm.

        Parameters
        ----------
        num_features : int, optional
            Number of features to learn for each movie (default is 10).
        normalized : bool, optional
            Whether to normalize the dataset or not (default is False).
        reg : float, optional
            Reguralization parameter (default is 1).
        Y : ndarray, optional
            The user-movie rating matrix where Y[i,j] is the rating given by
            user j on movie i.
        R : ndarray, optional
            The user-movie matrix such that R[i,j] = 1 if user j has rated
            movie i, and 0 otherwise.
        """
        self.num_features = num_features
        self.reg = reg
        self.Y = Y
        self.R = R
        self.Theta = None
        self.X = None
        self.normalized = normalized

    def learn(self, Y=None, R=None, num_features=None, reg=None, verbose=False,
              maxiter=DEFAULT_MAX_ITER, normalize=None, tol=1e-4):
        from . import utils

        # Set the variables first
        if Y is not None:
            self.Y = Y
        if R is not None:
            self.R = R
        if reg is not None:
            self.reg = reg
        if num_features is not None:
            self.num_features = num_features
        if normalize is not None:
            self.normalized = normalize

        # Prepare all the required local variables
        Y, R, num_features, reg = self.Y, self.R, self.num_features, self.reg
        if self.normalized:
            Y, self.Ymean = utils.normalize_ratings(self.Y, self.R)
            self.normalized = True
        num_movies, num_users = self.Y.shape

        # Initialize random parameters
        logging.info("Initializing random paramters...")
        initial_X = np.random.randn(num_movies, num_features)
        initial_Theta = np.random.randn(num_users, num_features)
        initial_params = np.append(
            initial_X.flatten(), initial_Theta.flatten())
        extra_args = (Y, R, num_features, reg)

        def callback(x):
            if verbose:
                sys.stdout.write('.')
                sys.stdout.flush()

        # Cost minimization
        logging.info("Running the optimizer...")
        result = minimize(
            fun=utils.cf_cost,
            x0=initial_params,
            args=extra_args,
            jac=True,
            method='CG',
            callback=callback,
            tol=tol,
            options={
                'maxiter': maxiter,
                'disp': verbose,
            })

        # Extract learned parameters
        self.X = np.reshape(
            result.x[:num_movies * num_features], (num_movies, num_features))
        self.Theta = np.reshape(
            result.x[num_movies * num_features:], (num_users, num_features))

        return self

    def recommendations(self, user_id, n=10):
        Ypredicted = np.dot(self.X, self.Theta.T)
        if self.normalized:
            Ypredicted += self.Ymean.reshape(-1, 1)
        user_predictions = Ypredicted[:, user_id].flatten()
        sorted_movie_ids = np.flip(user_predictions.argsort(), axis=0)
        result = []
        i = 0
        while len(result) < n:
            movie_id = sorted_movie_ids[i]
            if self.R[movie_id, user_id] == 0:
                result.append((movie_id, user_predictions[movie_id]))
            i += 1
        return result

    def save(self, filename):
        from . import utils
        logging.info("Saving recommender model to '{}'".format(filename))
        utils.save_to_file(self, filename)

    def load(filename):
        from . import utils
        logging.info("Loading recommender model from '{}'".format(filename))
        return utils.load_from_file(filename)
