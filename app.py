# This is the main app function that flask is going to serve
# Team 180 - DVA - Fall 2020

# import the necessary libraries
from flask import Flask, render_template

# import files from the project directory
import analyze
import api

app = Flask(__name__)

@app.route('/')
def home():
	events = api.get_events()
	aggregated_tweets = api.get_aggregated_tweets()
	# commenting this out for now, since it is much larger than we need. May want to random sample to reduce the amount of time it takes to load
	tweet_data = api.get_tweet_data()
	# tweet_data = []

	return render_template('home.html', events=events, aggregated_tweets=aggregated_tweets, tweet_data=tweet_data)

if __name__ == '__main__':
	app.run()