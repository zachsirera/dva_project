# This is a file to handle the analysis of our chosen dataset 
# Team 180 - DVA - Fall 2020

# import the necessary libraries
import csv
# import datetime
import textstat

from textblob import TextBlob




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

	return parse_tweets(tweet_list)


def parse_tweets(tweet_list: list):
	''' parse tweets, remove artifacts that can confuse analytical methods '''

	for index, tweet in enumerate(tweet_list):
		if tweet['text'] != None:
			tweet_separated = tweet['text'].split(" ")
			for word in tweet_separated:
				# print(word)
				try: 


					# Put any more parsing rules here 
					if word[0] == '@':
						tweet_separated.remove(word)
					if word[0] == '#':
						tweet_separated.remove(word)
					if word[0] == '&':
						tweet_separated.remove(word)
					if word[0] == '.':
						tweet_separated.remove(word)
					if word[0:4] == 'http':
						tweet_separated.remove(word)


				except IndexError:
					# Occasionally tweets contain a double space. This can be problematic when splitting on " "
					pass

			tweet_list[index]['text'] = " ".join(tweet_separated)


	return get_tweet_sentiment(tweet_list)




def get_tweet_sentiment(tweet_list: list):
	''' call textblob to get sentiment polarity and subjectivity ''' 

	for index, tweet in enumerate(tweet_list):
		try:
			blob = TextBlob(tweet['text'])
			tweet_list[index]['sentiment'] = blob.sentiment.polarity
			tweet_list[index]['subjectivity'] = blob.sentiment.subjectivity
		except TypeError:
			# Tweets with no text won't be analyzed
			pass


	return get_tweet_complexity(tweet_list)



def get_tweet_complexity(tweet_list: list):
	''' assess the complexity of tweet content ''' 
	for index, tweet in enumerate(tweet_list):
		try:
			tweet['reading_ease'] = textstat.flesch_reading_ease(tweet['text'])
			tweet['grade_level'] = textstat.flesch_kincaid_grade(tweet['text'])
		except TypeError:
			# Tweets with no text won't be analyzed
			pass

	return tweet_list


def group_tweets_by_month(tweet_list: list):
	''' aggregate tweetlist, group by month '''

	aggregated = dict()

	for tweet in tweet_list:
		try: 
			date = tweet['created_at'].split(" ")[0].split("-")

			try:
				month = f'{date[2]}-{date[0]}'
				data = aggregated[month] 
				new_subj = (data['count'] * data['subjectivity'] + tweet['subjectivity']) / (data['count'] + 1)
				new_sent = (data['count'] * data['sentiment'] + tweet['sentiment']) / (data['count'] + 1)
				new_reading = (data['count'] * data['reading_ease'] + tweet['reading_ease']) / (data['count'] + 1)
				new_grade = (data['count'] * data['grade_level'] + tweet['grade_level']) / (data['count'] + 1)
				data['count'] += 1
				data['subjectivity'] = new_subj
				data['sentiment'] = new_sent
				data['reading_ease'] = new_reading
				data['grade_level'] = new_grade
				aggregated[month] = data
			except KeyError:
				# Using this catch to add new objects to the dictionary
				aggregated[month] = {'count': 1, 'sentiment': float(tweet['sentiment']), 'subjectivity': float(tweet['subjectivity']),
				'reading_ease': float(tweet['reading_ease']), 'grade_level': float(tweet['grade_level'])}
			except IndexError:
				# Tweets with improperly formatted dates won't be aggregated 
				pass

		except AttributeError:
			# Tweets with no date won't be aggregated 
			pass

	return aggregated

def update_monthly_counts(aggregated: dict):
	''' update a csv with aggregated data ''' 

	csv_columns = ['month', 'count', 'sentiment', 'subjectivity', 'reading_ease', 'grade_level']

	try:
		with open('aggregated_tweets.csv', 'w', newline='') as f:
			csv_writer = csv.writer(f, delimiter=",")
			csv_writer.writerow(csv_columns)
			
			for data in aggregated:
				values = list(aggregated[data].values())
				values.insert(0, data)
				
				csv_writer.writerow(values)


	except IOError:
		print("IOError")

	return 




if __name__ == '__main__':
	tweet_list = read_csv('tweets.csv')
	aggregated = group_tweets_by_month(tweet_list)
	update_monthly_counts(aggregated)

	
