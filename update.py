# this is a function to get new tweets and add them to the "database"

# get the necessary external libraries
import os
import tweepy 
import csv
from datetime import datetime 

# get the files from the project library that we might needgbtfgh
import analyze
# import word_cloud



class TweetMiner(object):


	def __init__(self, consumer_key, consumer_secret, result_limit=3200):  

		auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)	
		self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
		self.result_limit = result_limit


	def mine_user_tweets(self, user, last_tweet_timestamp, mine_rewteets=False, max_pages=10):

		data = []
		page = 1
		date_format = '%m-%d-%Y %H:%M:%S'

		while page <= max_pages:
			statuses =  self.api.user_timeline(screen_name=user, count=self.result_limit, tweet_mode = 'extended', include_retweets=False)

			for item in statuses:

				if item.created_at > last_tweet_timestamp:

					mined = {
						'created_at': item.created_at.strftime(date_format),
						'text': item.full_text,
						'id_str': str(item.id),
						'favorite_count': item.favorite_count,
						'retweet_count': item.retweet_count,
						'is_retweet': 'false'
						# 'hashtags': item.entities['hashtags'],
						# 'status_count': item.user.statuses_count,
						# 'location': item.place,
					}

					last_tweet_id = item.id
					data.append(mined)

			page += 1

		# The twitter API returns random results, only way to ensure that there is the right number of results is to get more than we need and then remove duplicates
		# idk why this happens, it is so annoying. 

		seen = set()
		new_l = []

		for d in data:

			if d['id_str'] not in seen:
				seen.add(d['id_str'])
				new_l.append(d)

		return new_l







def read_csv(filename: str):
	''' read a csv into a list of dicts for ease of computations '''

	tweet_list = []

	ints = ['favorite_count', 'retweet_count', 'length']
	floats = ['sentiment', 'subjectivity', 'reading_ease', 'grade_level']

	with open(filename, 'r', encoding='utf-8') as f:
		csv_reader = csv.reader(f, delimiter=',')
		header_labels = list(next(csv_reader))

		for row in csv_reader:
			tweet = dict()
			for index, label in enumerate(header_labels):

				if label in ints:
					try:
						tweet[header_labels[index]] = int(row[index])
					except IndexError:
						tweet[header_labels[index]] = None
				elif label in floats: 
					try:
						tweet[header_labels[index]] = float(row[index])
					except IndexError:
						tweet[header_labels[index]] = None
				else:
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
	

	return max_date


def get_auth_creds():
	''' get auth creds from environment variables '''

	consumer_key = os.getenv('api_key')
	consumer_secret = os.getenv('api_secret')

	return consumer_key, consumer_secret 
	



def get_new_tweets(max_date, consumer_key, consumer_secret):
	''' make a call to the twitter API with Tweepy to get new tweets ''' 

	miner=TweetMiner(consumer_key=consumer_key, consumer_secret=consumer_secret, result_limit = 200)
	mined_tweets_dict = dict()
	
	return miner.mine_user_tweets(user = 'realDonaldTrump', last_tweet_timestamp=max_date, max_pages = 17)




def analyze_new_tweets(tweet_list: list):
	''' pass new tweets through the analysis algorithms ''' 

	return analyze.get_tweet_length(new_tweet_list)



def write_new_aggregated_tweets(tweet_list: list): 
	''' write new data to aggregated_tweets.csv'''

	aggregated_month = analyze.group_tweets_by_month(tweet_list)
	aggregated_subject = analyze.add_subject_aggregates(tweet_list)
	analyze.write_aggregated_csv(aggregated_month, aggregated_subject, 'new_data/aggregated_tweets.csv')

	return


def write_new_tweet_data(tweet_list: list): 
	''' write new data to tweet_data.csv '''

	analyze.write_data_csv(tweet_list, 'new_data/tweet_data.csv')

	return

def write_new_calendar_tweets(tweet_list: list)

	aggregated_day = analyze.group_tweets_by_day(tweet_list)
	aggregated_subject_day = analyze.add_subject_aggregates_day(tweet_list)

	write_calendar_csv(aggregated_day, aggregated_subject_day, 'new_data/calendar_tweets.csv')

	return


def update_word_clouds(tweet_list: list): 
	''' update word clouds with new data ''' 


	pass 




if __name__ == '__main__':
	# get old tweets already in the "database"
	old_tweet_list = read_csv('new_data/tweet_data.csv')

	# get the date of the last tweet in the database so we know where to stop
	date = get_last_tweet(old_tweet_list)
	print(date)

	# # get twitter auth creds from the environment and make a call to the twitter API to get new tweets 
	key, secret = get_auth_creds()
	new_tweet_list = get_new_tweets(date, key, secret)

	print(len(new_tweet_list))

	if len(new_tweet_list) != 0:

		# pass new tweets through the analyzing algorithms and append with old tweet data
		analyzed_new_tweets = analyze_new_tweets(new_tweet_list)
		updated_tweet_list = analyzed_new_tweets + old_tweet_list

		# write the combined data to the disk
		write_new_aggregated_tweets(updated_tweet_list)
		write_new_tweet_data(updated_tweet_list)
		# write_calendar_csv(updated_tweet_list)
	
	





