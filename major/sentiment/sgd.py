#!/bin/env python3

import random

import numpy as np


class SGD:

    def __init__(self, model, learning_rate=1e-2, batch_size=30, optimizer='adagrad'):
        self.model = model
        assert self.model is not None, "Please provide a model to optimize!"

        self.iter = 0
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.optimizer = optimizer.lower()

        if self.optimizer == 'sgd':
            print("Using sgd..")
        elif self.optimizer == 'adagrad':
            print("Using adagrad...")
            epsilon = 1e-8
            self.grads = [epsilon + np.zeros(W.shape) for W in self.model.stack]
        else:
            raise ValueError("Invalid optimizer")

        # initialize a variable to store all the costs
        self.costs = []
        self.expcosts = []

    def optimize(self, trees, log_interval=1):
        m = len(trees)

        # Randomly shuffle data
        random.shuffle(trees)

        it = 0
        for i in range(0, 1 + m - self.batch_size, self.batch_size):
            it += 1
            self.iter += 1

            data = trees[i: i+self.batch_size]
            cost, grad = self.model.cost_and_grad(data)

            self.costs.append(cost)

            # compute exponentially weighted cost
            if np.isfinite(cost):
                if self.iter > 1:
                    self.expcosts.append(0.01*cost + 0.99*self.expcosts[-1])
                else:
                    self.expcosts.append(cost)

            # Perform one step of parameter update
            if self.optimizer == 'sgd':
                scale = -self.learning_rate
                update = grad
            elif self.optimizer == 'adagrad':
                # trace = trace+grad.^2
                self.grads[1:] = [gt+g**2 for gt,g in zip(self.grads[1:], grad[1:])]
                # update = grad.*trace.^(-1/2)
                update = [g*(1./np.sqrt(gt)) for gt,g in zip(self.grads[1:], grad[1:])]
                # handle dictionary separately
                dL = grad[0]
                dLt = self.grads[0]
                for j in dL.keys():
                    dLt[:,j] = dLt[:,j] + dL[j]**2
                    dL[j] = dL[j] * (1./np.sqrt(dLt[:,j]))
                update = [dL] + update
                scale = -self.learning_rate

            self.model.update_params(scale=scale, update=update)

            # Log status
            if self.iter % log_interval == 0:
                print("\r   Iter = {} ({}), Cost = {:.4f}, Expected = {:.4f}".format(
                    it, self.iter, cost, self.expcosts[-1]), end=' ')
