from flask import Flask
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

@app.route('/')
def index():
    
  
    vs = SentimentIntensityAnalyzer()
    
    text = "Fuck this sprint"
    print(vs.polarity_scores(text))

    return 'Hello from Flask!'

app.run(host='0.0.0.0', port=81)