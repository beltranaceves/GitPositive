from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyzeCommits(commits):
    sentiment_analyzer = SentimentIntensityAnalyzer()
    for commit in commits:
      score = sentiment_analyzer.polarity_scores(commit["message"])
      commit["score"] = score
    return commits