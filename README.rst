SimpleBlog
==========

This is a showcase blog application implemented on Python Django framework.

Installation
------------

1. Create a virtual environment.
2. Clone the repository and cd into it.
3. Install the packages from the requirements.txt:

  pip install -r requirements.txt

4. Apply the database migrations:

  python simpleblog/manage.py migrate

5. Fill the database with the sample users and articles data:

  python simpleblog/manage.py loaddata

The data loading may take some time as:

* 50000 users are created.
* 5000 of them are authors with 10 posts each.
* Every user cast a random number of votes (up to 1000) for random posts.

All users are created with the password "123".
