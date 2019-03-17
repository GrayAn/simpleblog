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

All users are created with the password "123".
