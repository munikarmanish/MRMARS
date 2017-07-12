from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.core.urlresolvers import reverse
from django.contrib.postgres.fields import JSONField


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


class Movie(Timestampable):
    title = models.TextField()
    photo = models.ImageField()
    description = RichTextField()
    slug = models.SlugField(unique=True)
    released_date = models.DateField()
    genre = models.ManyToManyField(Genre)
    rating = models.FloatField(default=0)

    class Meta:
        ordering = ["slug", ]

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
        unique_together = (("user", "movie"),)

    def __str__(self):
        return self.user.username + self.movie.title


class Prediction(Timestampable):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    predicted = models.FloatField(default=0)
    is_already_rated = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + self.movie.title

    class Meta:
        unique_together = (("user", "movie"),)


class Data(models.Model):
    data = JSONField()

    def __str__(self):
        return 'Training data'
