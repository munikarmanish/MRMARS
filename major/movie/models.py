from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
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
    title = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    year = models.IntegerField(validators=[MinValueValidator(1900),
                                           MaxValueValidator(timezone.now().year)])
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.title


class Review(Timestampable):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.user.username + self.movie.title

    class Meta:
        unique_together = (("user", "movie"),)


class Recommendation(Timestampable):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    score = models.FloatField(default=0)

    def __str__(self):
        return self.user.username + self.movie.title

    class Meta:
        ordering = ['-score']
