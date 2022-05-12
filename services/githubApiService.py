import requests

def getRepositoriesByUsername(username):
    url = f'https://api.github.com/users/{username}/repos'
    response = requests.get(url)
    return response.json()

def getCommitsByRepositoryUrl(repoUrl) :
    url = f'{repoUrl}/commits'
    response = requests.get(url)
    return response.json()

def getCommitsByUsernameAndYear(username, year):
    repositories = getRepositoriesByUsername(username)
    commits = []
    print(repositories)
    for repository in repositories:
      repositoryCommits = getCommitsByRepositoryUrl(repository["url"])
      #Filter them by year
      for repositoryCommit in repositoryCommits:
        commitDate = repositoryCommit["commit"]["author"]["date"]
        commitYear = commitDate.split("-")[0]
        if commitYear == year:  
          commits.append(repositoryCommit)
    return commits