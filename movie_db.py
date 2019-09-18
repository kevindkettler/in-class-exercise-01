# Before running this flask app, you need to have done the following:
# 1) Installed pymysql Python module, and mysql client on VM
# 2) Created a SQL instance in GCP with (non-empty password)
# 3) Configured the SQL instance so that it accepts connections from
#    your VM's public IP address
# 4) Created a DB on your SQL instance named films with the schema:
#    name VARCHAR(40), year smallint, rating smallint
#
# When you first access the URL, go to the terminal on the VM and input
# the IP address of the SQL instance and the DB password.
#
# To start the app:
# export FLASK_APP=movie_db.py
# export FLASK_DEBUG=1
# python3 -m flask run --host=0.0.0.0 --port=8080

from flask import Flask
import getpass, pymysql, sys

app = Flask(__name__)
app.db = None

def connect_db():
    if not app.db:
        db_IP = input('Input DB server IP address: ')
        # getpass so that password is not echoed to the terminal
        pswd = getpass.getpass('Password: ')
        app.db = pymysql.connect(db_IP, 'root', pswd, 'films')
    else:
        print('Connected!', file=sys.stderr)

@app.route('/')
# Top-level route.  Connects to DB if not already connected.
def hello():
    if not app.db:
        connect_db()

    return 'Welcome to the movie DB.'

@app.route('/all_movies')
def get_movies():
    if not app.db:
        connect_db()

    # retrieve all the movies (a tuple of tuples)
    c = app.db.cursor()
    c.execute('SELECT * from movies')
    movie_list = c.fetchall()

    # To help with debugging, use stderr to output to terminal on VM
    print(movie_list, file=sys.stderr)
    movies = '<h2>'

    # Convert movie tuples into a giant string to return to browser
    for movie in movie_list:
        movies += movie[0] + ' ' + str(movie[1]) + ' ' + str(movie[2]) + '<br>'
    movies += '</h2>'

    # display movies in the browser in a very rudimentary way
    return movies

@app.route('/add_movie/<movie>')
def add_movie(movie):
    # assumes that movie entry in the URL follows the following format:
    # movie name:year:rating

    if not app.db:
        connect_db()

    # extract colon-separated tokens
    toks = movie.split(':')

    c = app.db.cursor()
    # construct the query to insert movie record into DB
    query = 'INSERT INTO movies values("{}", {}, {});'.format(
            toks[0], toks[1], toks[2])
    print(query, file=sys.stderr)
    c.execute(query)

    # commit the change to the DB
    app.db.commit()

    # function must return
    return '<h1>Record added.</h1>'
