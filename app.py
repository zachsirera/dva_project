# This is the main app function that flask is going to serve
# Team 180 - DVA - Fall 2020

# import the necessary libraries
from flask import Flask, render_template

import random

# import files from the project directory
import analyze
import api

app = Flask(__name__)


@app.route('/')
def cover():
	return render_template('cover.html')


@app.route('/index')
def home():
	events = api.get_events()
	aggregated_tweets = api.get_aggregated_tweets()
	# commenting this out for now, since it is much larger than we need. May want to random sample to reduce the amount of time it takes to load
	tweet_data = api.get_tweet_data()
	#reduced_tweet_data = random.sample(tweet_data, int(0.25 * len(tweet_data)))

	#Here I make sure I have at most the max allowed number of tweets by category
	#but keep all the tweets for those categories where we have fewere than the max
	#allowed
	topics = ['covid','economy','foreign_policy','impeachment','domestic_policy','other']

	reducedDict = {}

	maxTweetsPerTopic = 1586   #4940 gives about 25% of the data. 1586 gives 10%

	for workingTopic in topics:

		workingResults =  [x for x in tweet_data if x[workingTopic] == '1']
        
		reducedWorkingResults = random.sample(workingResults, min(maxTweetsPerTopic,len(workingResults)))
        
		dataAsDic = {x['id_str']:x for x in reducedWorkingResults}
        
		reducedDict.update(dataAsDic)
        
	keys = reducedDict.keys()
	reduced_tweet_data =  [reducedDict[wokingKey] for wokingKey in keys ]

	calendar_data = api.get_calendar()

	return render_template('home.html', events=events, aggregated_tweets=aggregated_tweets, tweet_data=reduced_tweet_data, calendar_data=calendar_data)


@app.route('/methodology')
def methodology():
	return render_template('methodology.html')



if __name__ == '__main__':
	app.run()