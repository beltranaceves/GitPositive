import os
import datetime

from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, jsonify
from flask_cors import CORS
from flask_github import GitHub

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import declarative_base


from services.githubApiService import getCommitsByUsername, getRepositoryCountByUsername
from services.sentimentService import analyzeCommits

app = Flask(__name__)
app.debug = True
CORS(app)
#Setup app config for GitHub login
app.config['GITHUB_CLIENT_ID'] = os.environ['GITHUB_CLIENT_ID']
app.config['GITHUB_CLIENT_SECRET'] = os.environ['GITHUB_CLIENT_SECRET']
app.secret_key = os.environ['GITHUB_CLIENT_ID']
app.config['SESSION_TYPE'] = 'filesystem'

github = GitHub(app)

# setup sqlalchemy

# Get the application's root directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create db directory under the main app directory
DB_DIR = os.path.join(BASE_DIR, 'db')
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# Set database path relative to app directory
DATABASE_URI = f'sqlite:///{os.path.join(DB_DIR, "github-flask.db")}'
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
  commits = getCommitsByUsername(g.user, github)
  return commits
  
def getCurrentUserCount():
  emailInfos = github.get('/user/emails')
  emails = []
  for emailInfo in emailInfos:
      emails.append(emailInfo['email'])
  g.user.github_emails = emails
  repo_count = getRepositoryCountByUsername(g.user, github)
  app.logger.info("WE WORK")
  print(g)
  return repo_count
  
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
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:81')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


def log_to_file(message):
    with open('app.log', 'a') as f:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'[{timestamp}] {message}\n')

# Usage example:
@app.route('/')
def index():
    return render_template('index.html')
    if g.user:
        log_to_file(f"User {g.user.github_login} accessed homepage")
        repo_count = getCurrentUserCount()
        return render_template('dashboard.html', username = g.user.github_login, repo_count = repo_count)
    else:
        return render_template('index.html')

cache_commits = None

@app.route('/contributions')
def contributions():
    global cache_commits
    if g.user:
      # Handle error when g.user is not logged in
      if not cache_commits:
        print("not using cache")
        commits = getCurrentUserCommits()
        cache_commits = commits
      else:
        print("using cache")
        commits = cache_commits     
    
      commit_count = commits.pop()
      analyzed_commits = analyzeCommits(commits)
      return render_template('contributions.html', username = g.user.github_login, title = "Default title", trait_desc = "You are the most true neutral dev in the world", commit_count = commit_count["total"], commits = analyzed_commits)
    else:
      return render_template('index.html')


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
    if session.get('user_id', None) is None or g.user is None:
        return github.authorize(scope="user:email, repo")
    else:
        repo_count = getCurrentUserCount()
        return render_template('dashboard.html', username = g.user.github_login, repo_count = repo_count)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/user')
def user():
    return jsonify(github.get('/user'))


@app.route('/repo')
def repo():
    return jsonify(github.get('/repos/beltranaceves/gitpositive'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=81)



