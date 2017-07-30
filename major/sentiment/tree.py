import os
import pickle
from collections import defaultdict

from django.conf import settings
from nltk.parse import CoreNLPParser
from nltk.tree import ParentedTree
from pycorenlp import StanfordCoreNLP

try:
    CORENLP_SERVER = settings.CORENLP_SERVER
except AttributeError:
    CORENLP_SERVER = 'http://localhost:9000'
CoreNLP = StanfordCoreNLP(CORENLP_SERVER)

UNK = 'UNK'

WORD_MAP_FILENAME = 'models/word_map.pickle'


def parse(text):
    parser = CoreNLPParser(CORENLP_SERVER)
    result = parser.raw_parse(text)
    trees = [tree for tree in result]
    for tree in trees:
        tree.chomsky_normal_form()
        tree.collapse_unary(collapseRoot=True, collapsePOS=True)
    trees = [ParentedTree.convert(tree) for tree in trees]
    return trees


def isleaf(tree):
    return isinstance(tree, ParentedTree) and tree.height() == 2


def traverse(tree, f=print, args=None, leaves=False):
    if leaves:
        if isleaf(tree):
            f(tree, args)
            return
    else:
        f(tree, args)
        if isleaf(tree):
            return
    for child in tree:
        traverse(child, f, args)


def build_word_map():
    print("Building word map...")
    with open("trees/train.txt", "r") as f:
        trees = [ParentedTree.fromstring(line) for line in f]

    print("Counting words...")
    words = defaultdict(int)
    for tree in trees:
        for token in tree.leaves():
            words[token] += 1

    word_map = dict(zip(words.keys(), range(len(words))))
    word_map[UNK] = len(words)  # Add unknown as word
    with open(WORD_MAP_FILENAME, 'wb') as f:
        pickle.dump(word_map, f)
    return word_map


def load_word_map():
    if not os.path.isfile(WORD_MAP_FILENAME):
        return build_word_map()
    print("Loading word map...")
    with open(WORD_MAP_FILENAME, 'rb') as f:
        return pickle.load(f)


def load_trees(dataset='train'):
    filename = "trees/{}.txt".format(dataset)
    with open(filename, 'r') as f:
        print("Reading '{}'...".format(filename))
        trees = [ParentedTree.fromstring(line) for line in f]
    return trees


if __name__ == '__main__':
    word_map = load_word_map()
