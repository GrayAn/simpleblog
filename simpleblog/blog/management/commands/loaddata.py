import csv
import datetime
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from ...models import Post


class Command(BaseCommand):
    help = 'Loads dummy authors and posts to the database'

    def handle(self, *args, **options):
        users = {user.username: user for user in User.objects.all()}

        current_directory = os.path.dirname(os.path.realpath(__file__))
        data_directory = os.path.normpath(os.path.join(current_directory, '..', '..', '..', 'data'))

        authors_file_path = os.path.join(data_directory, 'authors.csv')
        articles_file_path = os.path.join(data_directory, 'articles.csv')

        with open(authors_file_path, 'r') as f:

            reader = csv.DictReader(f)
            for row in reader:
                if row['login'] not in users:

                    user = User()
                    user.username = row['login']
                    user.first_name = row['firstname']
                    user.last_name = row['lastname']
                    user.email = row['email']
                    user.set_password('123')
                    user.is_staff = True
                    user.save()
                    users[user.username] = user

        self.stdout.write(self.style.SUCCESS('Authors were uploaded'))

        with open(articles_file_path, 'r') as f:

            reader = csv.DictReader(f)
            for row in reader:

                if row['login'] not in users:
                    raise CommandError('User {} does not exist'.format(row['login']))

                user = users[row['login']]

                try:
                    post = Post.objects.get(author=user, title=row['title'])
                except Post.DoesNotExist:
                    post = Post()
                    post.author = user
                    post.title = row['title']

                dt = datetime.datetime.strptime(row['date'], '%Y-%m-%dT%H:%M:%S')
                post.created = dt.replace(tzinfo=datetime.timezone.utc)
                post.text = row['text']
                post.save()

        self.stdout.write(self.style.SUCCESS('Articles were uploaded'))
