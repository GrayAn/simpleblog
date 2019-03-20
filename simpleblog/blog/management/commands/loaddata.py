from datetime import datetime, timedelta
from random import normalvariate, random

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from ...models import Post, Vote


# Total number of users
USERS_NUMBER = 50000
# Number of authors among users
AUTHORS_NUMBER = 5000
# Number of posts every author has
POSTS_BY_AUTHOR = 10

# Number of votes of a user is calculated
# as normal distribution in the random_vote_number function
MAX_VOTES_BY_USER = 1000

# Number of inserts in a bulk create request
INSERTS_BY_REQUEST = 500


def random_post(first_post_id):
    n = normalvariate(0, 0.2)
    total = AUTHORS_NUMBER * POSTS_BY_AUTHOR
    offset = total // 2 + int(n * total) // 5
    return first_post_id + min(offset, total)


def random_vote_number():
    n = normalvariate(0.5, 0.5)
    return max(int(MAX_VOTES_BY_USER * n / 3), 0)


class Command(BaseCommand):
    help = 'Loads dummy authors and posts to the database'

    def handle(self, *args, **options):
        password_hash = make_password('123')
        users = []
        for i in range(USERS_NUMBER):

            user = User()
            user.username = 'user{:05}'.format(i)
            user.email = '{}@simpleblog.org'.format(user.username)
            user.password = password_hash
            user.is_staff = True
            users.append(user)

            if len(users) == INSERTS_BY_REQUEST:
                User.objects.bulk_create(users)
                users = []

        if users:
            User.objects.bulk_create(users)
        del users

        self.stdout.write(self.style.SUCCESS('Users were created'))

        first_user_id = User.objects.order_by('id')[0].id

        dt = datetime(2018, 1, 1)
        posts = []
        for i in range(first_user_id, first_user_id + AUTHORS_NUMBER):
            for j in range(POSTS_BY_AUTHOR):

                post = Post()
                post.author_id = i
                post.title = 'Post #{}-{}'.format(i, j)
                post.text = 'Post #{}-{} data\n'.format(i, j) * 50
                post.created = dt + timedelta(seconds=i * POSTS_BY_AUTHOR + j)
                posts.append(post)

                if len(posts) == INSERTS_BY_REQUEST:
                    Post.objects.bulk_create(posts)
                    posts = []

        if posts:
            Post.objects.bulk_create(posts)
        del posts

        self.stdout.write(self.style.SUCCESS('Posts were created'))

        first_post_id = Post.objects.order_by('id')[0].id

        for i in range(USERS_NUMBER):
            vote_number = random_vote_number()
            votes = {}
            for j in range(vote_number):

                post_id = random_post(first_post_id)
                if post_id in votes:
                    continue

                vote = Vote()
                vote.author_id = first_user_id + i
                vote.post_id = post_id
                vote.up = random() > 0.1
                votes[post_id] = vote

            Vote.objects.bulk_create(votes.values())

            if i % 1000 == 0 and i:
                self.stdout.write('Votes for {} users were created'.format(i))

        self.stdout.write(self.style.SUCCESS('Votes were created'))

        for post in Post.objects.all():
            upvotes = Vote.objects.filter(post=post, up=True).count()
            downvotes = Vote.objects.filter(post=post, up=False).count()
            if upvotes or downvotes:
                post.upvotes = upvotes
                post.downvotes = downvotes
                post.rating = upvotes - downvotes
                post.save()

        self.stdout.write(self.style.SUCCESS('Post ratings were updated'))
