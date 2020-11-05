# this is a function to get new tweets and add them to the "database"

# get the necessary external libraries
import os
import tweepy as tw
import csv
from datetime import datetime 

# get the files from the project library that we might needgbtfgh
import analyze
import wordcloud


def read_csv(filename: str):
	''' read a csv into a list of dicts for ease of computations '''

	tweet_list = []

	with open(filename, 'r') as f:
		csv_reader = csv.reader(f, delimiter=',')
		header_labels = list(next(csv_reader))

		for row in csv_reader:
			tweet = dict()
			for index, label in enumerate(header_labels):
				try:
					tweet[header_labels[index]] = row[index]
				except IndexError:
					tweet[header_labels[index]] = None
			tweet_list.append(tweet)

	return tweet_list



def get_last_tweet(tweet_list: list):
	''' get the most recent tweet that is already stored so we know where to stop the API calls. '''

	date_format = '%m-%d-%Y %H:%M:%S'
	max_date = max([datetime.strptime(x['created_at'], date_format) for x in tweet_list])
	
	for tweet in tweet_list:
		if tweet['created_at'] == max_date.strftime(date_format):
			max_id_str = tweet['id_str']

	return max_date, max_id_str


def get_auth_creds():
	''' get auth creds from environment variables '''

	consumer_key = os.getenv('')
	consumer_secret = os.getenv('')
	access_token = os.getenv('')
	access_token_secret = os.getenv('')

	return consumer_key, consumer_secret, access_token, access_token_secret
	



def get_new_tweets(max_date, max_id_str, consumer_key, consumer_secret, access_token, access_token_secret):
	''' make a call to the twitter API with Tweepy to get new tweets ''' 

	# waiting on my Twitter developer account to get approved 

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	api = tweepy.API(auth)

	pass 



def analyze_new_tweets(tweet_list: list):
	''' pass new tweets through the analysis algorithms ''' 

	pass



def write_new_aggregated_tweets(tweet_list: list): 
	''' write new data to aggregated_tweets.csv'''

	pass 



def write_new_tweet_data(tweet_list: list): 
	''' write new data to tweet_data.csv '''

	pass



def update_word_clouds(tweet_list: list): 
	''' update word clouds with new data ''' 


	pass 




if __name__ == '__main__':
	old_tweet_list = read_csv('new_data/tweet_data.csv')
	date, id_str = get_last_tweet(old_tweet_list)
	print(date, id_str)
	# consumer_key, consumer_secret, access_token, access_token_secret = get_auth_creds()
	





