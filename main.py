import os

from flask import Flask, request, g, session, redirect, url_for
from flask import render_template_string, render_template, jsonify
from flask_cors import CORS
from flask_github import GitHub

from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from services.githubApiService import getCommitsByUsernameAndYear

app = Flask(__name__)
CORS(app)
#Setup app config for GitHub login
app.config['GITHUB_CLIENT_ID'] = os.environ['GITHUB_CLIENT_ID']
app.config['GITHUB_CLIENT_SECRET'] = os.environ['GITHUB_CLIENT_SECRET']
app.secret_key = os.environ['GITHUB_CLIENT_ID']
app.config['SESSION_TYPE'] = 'filesystem'

github = GitHub(app)

# setup sqlalchemy
DATABASE_URI = 'sqlite:////tmp/github-flask.db'
engine = create_engine(DATABASE_URI)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

#TODO: research "already logged in" bug, maybe forze a logout and re-entry
def init_db():
    Base.metadata.create_all(bind=engine)

def getCurrentUserCommits():
  emailInfos = github.get('/user/emails')
  emails = []
  for emailInfo in emailInfos:
      emails.append(emailInfo['email'])
  g.user.github_emails = emails
  commits = getCommitsByUsernameAndYear(g.user, github)
  return commits
  
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    github_access_token = Column(String(255))
    github_id = Column(Integer)
    github_login = Column(String(255))
  
    def __init__(self, github_access_token):
        self.github_access_token = github_access_token


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.after_request
def after_request(response):
    db_session.remove()
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8080')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.route('/')
def index():
    if g.user:
        return render_template('calendar.html', username = g.user.github_login)
    else:
        return render_template('index.html')

@app.route('/contributions')
def contributions():
    # Handle error when g.user is not logged in
    emailInfos = github.get('/user/emails')
    emails = []
    for emailInfo in emailInfos:
        emails.append(emailInfo['email'])
    g.user.github_emails = emails
    #commits = getCommitsByUsernameAndYear(g.user, github)
    #return jsonify(commits)
    return render_template('analisis.html', username = g.user.github_login, title = "Default title", trait_desc = "You are the most true neutral dev in the world", commit_count = 9999)


@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token


@app.route('/github-callback')
@github.authorized_handler
def authorized(access_token):
    next_url = request.args.get('next') or url_for('index')
    if access_token is None:
        return redirect(next_url)

    user = User.query.filter_by(github_access_token=access_token).first()
    if user is None:
        user = User(access_token)
        db_session.add(user)

    user.github_access_token = access_token

    # Not necessary to get these details here
    # but it helps humans to identify users easily.
    g.user = user
    github_user = github.get('/user')
    user.github_id = github_user['id']
    user.github_login = github_user['login']
    user.github_name = github_user['name']
  
    db_session.commit()

    session['user_id'] = user.id
    return redirect(next_url)
  
@app.route('/login')
def login():
    if session.get('user_id', None) is None:
        return github.authorize(scope="user:email")
    else:
        # Handle error when g.user is not logged in
        return render_template('calendar.html', username = g.user.github_login)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/user')
def user():
    return jsonify(github.get('/user'))


@app.route('/repo')
def repo():
    return jsonify(github.get('/repos/cenkalti/github-flask'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=81)



