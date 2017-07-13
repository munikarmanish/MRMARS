#!/bin/env python3

import logging
import sys
from test import RecommenderTest

from utils import load_from_file

NUM_FEATURES = 10


def main():
    RecommenderTest().test_recommendation()


if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stderr, format='[%(levelname)s] :: %(message)s',
        level=logging.NOTSET)
    main()
