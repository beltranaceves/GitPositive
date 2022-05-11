import requests
def getRepositoriesByUsername(username):
    url = f'https://api.github.com/users/{username}/repos'
    response = requests.get(url)
    return response.json()

def getCommitsByRepositoryUrlAndYear(repoUrl) :
    url = f'{repoUrl}/commits'
    response = requests.get(url)
    return response.json()