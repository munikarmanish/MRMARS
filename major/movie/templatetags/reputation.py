from django import template
from movie.models import Review, Vote
register = template.Library()


@register.filter(name='reputation')
def reputation(user):
    reviews = Review.objects.filter(user=user)
    voteUp = 0
    voteDown = 0
    for review in reviews:
        votes = Vote.objects.filter(review=review)
        downVotes = votes.filter(up=False)
        upVotes = votes.filter(up=True)
        voteUp += len(upVotes)
        voteDown += len(downVotes)
    return (voteUp - voteDown)
