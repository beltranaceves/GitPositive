from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import defaultdict
from dateutil import parser

def average(lst):
    return sum(lst) / len(lst)
  
def normalizeCommits(commits):
  dates = defaultdict(lambda: [])
  for commit in commits:
    date = commit["date"].split("T")[0]
    commit["date"] = date
    dates[date].append(commit["score"]["compound"])

  timestamps = []
  iso = "T15:07:50Z"
  for date in dates.keys():
    averages = average(dates[date])
    timestamp = date+iso
    timestamp = parser.parse(timestamp)
    if averages <= -0.5: #very neg
      timestamps.append({
        "timestamp": timestamp,
        "count": 1
      })
    if averages < 0 and averages > -0.5: #slight neg
      timestamps.append({
        "timestamp": timestamp,
        "count": 2
      })
    if averages == 0: # Neutral
      timestamps.append({
        "timestamp": timestamp,
        "count": 3
      })
    if averages > 0 and averages < 0.5: #slight pos
      timestamps.append({
        "timestamp": timestamp,
        "count": 4
      })
    if averages >= 0.5: #very pos
      timestamps.append({
        "timestamp": timestamp,
        "count": 5
      })
    
  return timestamps

def analyzeCommits(commits):
    sentimentAnalyzer = SentimentIntensityAnalyzer()
    for commit in commits:
      score = sentimentAnalyzer.polarity_scores(commit["message"])
      commit["score"] = score
    timestamps = normalizeCommits(commits)
    return timestamps