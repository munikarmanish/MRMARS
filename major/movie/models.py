from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor.fields import RichTextField
from django.core.urlresolvers import reverse


# Create your models here.


class Timestampable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted_at = timezone.now()
        super().save()

    @cached_property
    def is_deleted(self):
        return timezone.now() > self.deleted_at


class Genre(Timestampable):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


def uploadPhoto(instance, filename):
    return "%s/%s/%s" % ('movie', instance.title, filename)


class Movie(Timestampable):
    title = models.CharField(max_length=255)
    photo = models.ImageField(upload_to=uploadPhoto)
    description = RichTextField()
    slug = models.SlugField(unique=True)
    released_date = models.DateField()
    genre = models.ManyToManyField(Genre)
    rating = models.FloatField(default=0)

    def get_absolute_url(self):
        return reverse("movie:movieDetail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class Review(Timestampable):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    summary = models.CharField(max_length=255)
    review = models.TextField(null=True, blank=True)
    rating = models.FloatField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.username + self.movie.title


class Recommendation(Timestampable):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    score = models.FloatField(default=0)

    def __str__(self):
        return self.user.username + self.movie.title

    class Meta:
        ordering = ['-score']
