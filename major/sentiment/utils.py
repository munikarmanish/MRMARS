import numpy as np
from django.conf import settings
from pycorenlp import StanfordCoreNLP

try:
    CORENLP_SERVER = settings.CORENLP_SERVER
except AttributeError:
    CORENLP_SERVER = 'http://localhost:9000'
CoreNLP = StanfordCoreNLP(CORENLP_SERVER)


def sentiment_from_rating(rating):
    if rating <= 1.7:
        return "Very Negative"
    elif rating <= 2.6:
        return "Negative"
    elif rating <= 3.4:
        return "Neutral"
    elif rating <= 4.3:
        return "Positive"
    elif rating <= 5.0:
        return "Very Positive"
    else:
        raise ValueError("Rating out of range")


def rating_from_sentiment(sentiment):
    sentiment = sentiment.lower()
    if sentiment == 'verynegative':
        return 1
    elif sentiment == 'negative':
        return 2
    elif sentiment == 'neutral':
        return 3
    elif sentiment == 'positive':
        return 4
    elif sentiment == 'verypositive':
        return 5
    else:
        raise AttributeError("Undefined sentiment")


def sentences(review):
    result = CoreNLP.annotate(
        review, properties={'annotators': 'sentiment', 'outputFormat': 'json'})
    return result['sentences']


def sentiments(review):
    sentiment_list = [s['sentiment'] for s in sentences(review)]
    return sentiment_list


def rating(review):
    sentiment_list = sentiments(review)
    return np.mean([rating_from_sentiment(s) for s in sentiment_list])
