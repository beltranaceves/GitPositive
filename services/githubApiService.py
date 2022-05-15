import datetime
from dateutil.relativedelta import relativedelta

def getRepoNameFromUrl(url):
    return url["name"]

def getRepositoriesByUsername(user, github):
    url = f'/users/{user.github_login}/repos'
    repos = github.get(url)
    repos = list(map(getRepoNameFromUrl, repos))
    return repos

def getCommitsByRepositoryUrl(repoName, user, github) :
    url = f'/repos/{user.github_login}/{repoName}/commits'
    yearAgo = datetime.datetime.now() - relativedelta(years=1)
  
    commits = github.get(url, params = {'author': user.github_login, 'since': yearAgo, 'per_page': 100, 'page': 1})  
    totalCommits = commits
    page = 2
    while commits != []:
      commits = github.get(url, params = {'author': user.github_login, 'since': yearAgo, 'per_page': 100, 'page': page})
      totalCommits += commits
    return totalCommits

def getCommitsByUsernameAndYear(user, github):
    repositoryNames = getRepositoriesByUsername(user, github)
    commits = []
    for repositoryName in repositoryNames:
      commits += getCommitsByRepositoryUrl(repositoryName, user, github)
    return commits