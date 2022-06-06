from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyzeCommits(commits):
    sentiment_analyzer = SentimentIntensityAnalyzer()
    results = []
    for commit in commits:
      results.append([commit,sentiment_analyzer.polarity_scores(commit)])
    return commits