from json import dumps, loads
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Data, Review, Movie


@receiver(post_save, sender=Review)
def create_data(sender, instance, *args, **kwargs):
    reviews = Review.objects.filter(movie=instance.movie)
    movie = Movie.objects.get(slug=instance.movie.slug)
    count = len(reviews)
    rating = 0
    for review in reviews:
        rating = rating + review.rating
    movie.rating = rating / count
    movie.save()
    temp = {}
    data = Data.objects.all().first()

    if data:
        temp = loads(data.data)
        if instance.user.username in temp.keys():
            temp[instance.user.username].setdefault(
                instance.movie.slug, 0)
            temp[instance.user.username][
                instance.movie.slug] = instance.rating
        else:
            temp.setdefault(instance.user.username, {})
            temp[instance.user.username].setdefault(
                instance.movie.slug, 0)
            temp[instance.user.username][
                instance.movie.slug] = instance.rating
        data.data = dumps(temp)
        data.save()
    else:
        temp.setdefault(instance.user.username, {})
        temp[instance.user.username].setdefault(instance.movie.slug, 0)
        temp[instance.user.username][
            instance.movie.slug] = instance.rating
        data = Data(data=dumps(temp))
        data.save()
