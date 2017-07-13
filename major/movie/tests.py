#!/bin/env python3

import logging
import os
import sys
import unittest

import numpy as np
from scipy.io import loadmat

from movie import recommender, utils
from django.conf import settings


class RecommenderTest(unittest.TestCase):

    def test_learn_and_save(self):
        # num_users, num_movies, num_features = 10, 10, 5
        R = utils.load_from_file('data/R.bin').astype(float)
        Y = utils.load_from_file('data/Y.bin')

        model = recommender.Recommender(Y=Y, R=R, reg=10, num_features=10)
        model.learn(maxiter=10, verbose=True)
        X, Theta = model.X, model.Theta

        filename = "models/recommender.bin"
        model.save(filename)
        model = recommender.Recommender.load(filename)
        np.testing.assert_almost_equal(X, model.X, decimal=2)
        np.testing.assert_almost_equal(Theta, model.Theta, decimal=2)

    def test_recommendation(self):
        movies = utils.load_movie_list()
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
        y_file = os.path.join(settings.BASE_DIR, "movie", "data", "Y.bin")
        r_file = os.path.join(settings.BASE_DIR, "movie", "data", "R.bin")
        R = utils.load_from_file(r_file)
        Y = utils.load_from_file(y_file).astype(float)
        Y = np.column_stack((my_ratings, Y))
        R = np.column_stack((my_ratings != 0, R))

        model = recommender.Recommender(Y=Y, R=R, reg=10, num_features=10)
        model.learn(maxiter=200, verbose=True, normalize=False, tol=1e-1)
        user_id = 0
        rated_ids = [i for i in range(Y.shape[0]) if R[i, user_id] == 1]
        logging.info("USER {} HAS RATED:".format(user_id))
        rated = []
        for i in rated_ids:
            # logging.info("   RATED <{:.1f}> FOR '{}'".format(
            #     Y[i, user_id], movies[i]))
            rated.append("   RATED <{:.1f}> FOR '{}'".format(
                Y[i, user_id], movies[i]))
        recommendations = model.recommendations(user_id=user_id)
        logging.info("RECOMMENDATIONS:")
        result = []
        for (i, rating) in recommendations:
            # logging.info("   <{:.1f}> {}".format(rating, movies[i]))
            result.append("   <{:.1f}> {}".format(rating, movies[i]))

        return rated, result


class CostFunctionTest(unittest.TestCase):

    def test_numerical_gradient(self):
        x = np.random.random((3, 3))
        grad = 2 * x
        numgrad = utils.numerical_grad(lambda x: np.sum(x**2), x)
        np.testing.assert_almost_equal(grad, numgrad)

    def test_cf_cost(self):
        # logging.info("Loading dataset...")
        R = utils.load_from_file('data/R.bin')
        Y = utils.load_from_file('data/Y.bin')

        # logging.info("Loading pre-trained parameters...")
        _ = loadmat('data/movie_params.mat')
        X = _.get('X')
        Theta = _.get('Theta')

        # reduce dataset
        num_users = 4
        num_movies = 5
        num_features = 3
        X = X[:num_movies, :num_features]
        Theta = Theta[:num_users, :num_features]
        Y = Y[:num_movies, :num_users]
        R = R[:num_movies, :num_users]

        params = np.append(X.flatten(), Theta.flatten())
        cost = utils.cf_cost(params=params, Y=Y, R=R,
                             num_features=num_features, reg=0)[0]
        # logging.info("Expected cost = 22.22")
        # logging.info("Computed cost = {:.2f}".format(cost))
        self.assertAlmostEqual(22.22, cost, places=2)

    def test_cf_gradient_without_regularization(self):
        # Create small problem
        num_users, num_movies, num_features = 4, 5, 3
        X_t = np.random.random((num_movies, num_features))
        Theta_t = np.random.random((num_users, num_features))
        Y = np.dot(X_t, Theta_t.T)
        self.assertEqual((num_movies, num_users), Y.shape)
        Y[np.random.random(Y.shape) > 0.5] = 0
        R = np.zeros_like(Y)
        R[Y != 0] = 1

        X = np.random.standard_normal(X_t.shape)
        Theta = np.random.standard_normal(Theta_t.shape)
        params = np.append(X.flatten(), Theta.flatten())
        numgrad = utils.numerical_grad(
            lambda x: utils.cf_cost(x, Y, R, num_features, reg=0)[0], params)
        J, grad = utils.cf_cost(params, Y, R, num_features, reg=0)
        np.testing.assert_almost_equal(numgrad, grad, decimal=2)

    def test_cf_cost_regularization(self):
        # logging.info("Loading dataset...")
        R = utils.load_from_file('data/R.bin')
        Y = utils.load_from_file('data/Y.bin')

        # logging.info("Loading pre-trained parameters...")
        _ = loadmat('data/movie_params.mat')
        X = _.get('X')
        Theta = _.get('Theta')

        # reduce dataset
        num_users = 4
        num_movies = 5
        num_features = 3
        X = X[:num_movies, :num_features]
        Theta = Theta[:num_users, :num_features]
        Y = Y[:num_movies, :num_users]
        R = R[:num_movies, :num_users]

        params = np.append(X.flatten(), Theta.flatten())
        cost = utils.cf_cost(params=params, Y=Y, R=R,
                             num_features=num_features, reg=1.5)[0]
        self.assertAlmostEqual(31.34, cost, places=2)

    def test_cf_gradient_regularization(self):
        # Create small problem
        num_users, num_movies, num_features = 4, 5, 3
        X_t = np.random.random((num_movies, num_features))
        Theta_t = np.random.random((num_users, num_features))
        Y = np.dot(X_t, Theta_t.T)
        self.assertEqual((num_movies, num_users), Y.shape)
        Y[np.random.random(Y.shape) > 0.5] = 0
        R = np.zeros_like(Y)
        R[Y != 0] = 1

        X = np.random.standard_normal(X_t.shape)
        Theta = np.random.standard_normal(Theta_t.shape)
        params = np.append(X.flatten(), Theta.flatten())
        reg = 1.5
        numgrad = utils.numerical_grad(
            lambda x: utils.cf_cost(x, Y, R, num_features, reg=reg)[0], params)
        J, grad = utils.cf_cost(params, Y, R, num_features, reg=reg)
        np.testing.assert_almost_equal(numgrad, grad, decimal=2)


class UtilsTest(unittest.TestCase):

    def test_rating_normalization(self):
        Y = utils.load_from_file('data/Y.bin')[:10, :10]
        R = utils.load_from_file('data/R.bin')[:10, :10]
        Ynorm, Ymean = utils.normalize_ratings(Y, R)
        Ymean_target = np.array(
            [4.2, 3, 4, 4, 3, 5, 3.66666667, 3.33333333, 4.5, 3])
        np.testing.assert_almost_equal(Ymean, Ymean_target, decimal=2)

    def test_load_movie_names(self):
        movie_list = utils.load_movie_list()
        for i in range(10):
            logging.info("   MOVIE = {}".format(movie_list[i]))


if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stderr, format='[%(levelname)s] :: %(message)s',
        level=logging.NOTSET)
    unittest.main()
