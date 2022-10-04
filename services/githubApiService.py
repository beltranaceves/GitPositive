import datetime
from dateutil.relativedelta import relativedelta

def getRepoNameFromDict(url):
    return url["name"]

def getRepoUrlFromDict(url):
    return url["url"]

def simplifyCommit(commit):
    simple = {}
    simple['message'] = commit['commit']['message']
    simple['date'] = commit['commit']['author']['date']
    return simple

def getRepositoriesByUsername2(user, github):
    url = f'/users/{user.github_login}/repos'
    repos = github.get(url)
    repos = list(map(getRepoNameFromDict, repos))
    return repos

def getRepositoriesByUsername(user, github):
    url = f'/user/repos'
    repos = github.get(url)
    repoUrls = list(map(getRepoUrlFromDict, repos))
    return repoUrls

def getCommitsByRepositoryUrl(repoUrl, user, github) :
    url = repoUrl + "/commits"
    yearAgo = datetime.datetime.now() - relativedelta(years=1)

    totalCommits = []
    for email in user.github_emails:
      commits = github.get(url, params = {'author': email, 'since': yearAgo, 'per_page': 100, 'page': 1})  
      totalCommits += commits
      page = 2
      while commits != []:
        commits = github.get(url, params = {'author': user.github_login, 'since': yearAgo, 'per_page': 100,         'page': page})
        page += 1
        totalCommits += commits
    return totalCommits

def getCommitsByUsername(user, github):
    repositoryUrls = getRepositoriesByUsername(user, github)
    commits = []
    for repositoryUrl in repositoryUrls:
      new_commits = getCommitsByRepositoryUrl(repositoryUrl, user, github)
      if new_commits != []:
        commits += new_commits
    commits = list(map(simplifyCommit, commits))
    return commits + [{'total': len(commits)}]

def getRepositoryCountByUsername(user, github):
    repositoryNames = getRepositoriesByUsername(user, github)
    return len(repositoryNames)