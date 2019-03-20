from django.contrib.auth.models import User
from django.db import models, transaction
from django.urls import reverse


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse('blog:details', args=(str(self.id),))

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=('created',)),
            models.Index(fields=('rating',)),
        ]


class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    up = models.BooleanField()

    class Meta:
        unique_together = ('post', 'author')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.pk is None:
            if self.up:
                self.post.upvotes += 1
                self.post.rating += 1
            else:
                self.post.downvotes += 1
                self.post.rating -= 1
            with transaction.atomic():
                self.post.save()
                return super().save(force_insert=force_insert, force_update=force_update,
                                    using=using, update_fields=update_fields)
        return super().save(force_insert=force_insert, force_update=force_update,
                            using=using, update_fields=update_fields)

    def delete(self, using=None, keep_parents=False):
        if self.up:
            self.post.upvotes -= 1
            self.post.rating -= 1
        else:
            self.post.downvotes -= 1
            self.post.rating += 1
        with transaction.atomic():
            self.post.save()
            return super().delete(using=using, keep_parents=keep_parents)
