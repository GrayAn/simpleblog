import datetime

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    text = models.TextField()
    created = models.DateTimeField()

    def get_absolute_url(self):
        return reverse('blog:details', args=(str(self.id),))

    @property
    def rating(self):
        return sum(1 if vote.up else -1 for vote in self.vote_set.all())

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.id and not self.created:
            self.created = datetime.datetime.utcnow()
        return super().save(force_insert=force_insert, force_update=force_update,
                            using=using, update_fields=update_fields)


class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    up = models.BooleanField()

    class Meta:
        unique_together = ('post', 'author')
