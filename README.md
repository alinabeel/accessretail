# Insights Labz

Deployment Steps
===========

Clone Repo:

    $ git clone git@github.com:alinabeel/insightslabz.git

After cloning the repository, create a virtualenv environment and install the prerequisites:

    $ python -m venv env
    $ source env/bin/activate
    $ pip install -r requirements.txt

Create migrations and migrate models into database:

    $ python ./manage.py makemigrations
    $ python ./manage.py migrate

Create superuser:

    $ python ./manage.py createsuperuser
    
Run Server:

    $ python manage.py runserver

Now you can login to admin panel by:

    # Browse http://localhost:8000/admin
    # Browse http://localhost:8000/superadmin
    


