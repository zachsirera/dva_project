# This is a file to handle the analysis of our chosen dataset 
# Team 180 - DVA - Fall 2020

# import the necessary libraries
import csv
import string
import textstat
from datetime import datetime

from textblob import TextBlob

from collections import Counter

# import files from the project directory
import classify




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

	return get_tweet_length(tweet_list)



def get_tweet_length(tweet_list: list):
	''' get the length of each tweet before parsing '''

	for index, tweet in enumerate(tweet_list):
		if tweet['text'] != None:
			tweet['length'] = len(tweet['text'])

	return parse_tweets(tweet_list)



def parse_tweets(tweet_list: list):
	''' parse tweets, remove artifacts that can confuse analytical methods '''

	for index, tweet in enumerate(tweet_list):
		if tweet['text'] != None:
			tweet_separated = tweet['text'].split(" ")
			tweet_separated = clean_characters(tweet_separated)

			# Join the tweet back together and strip out any remaining punctuation
			# tweet_joined = " ".join(tweet_separated) 
			# tweet_list[index]['text'] = tweet_joined.translate(str.maketrans('', '', string.punctuation))

			# parse tweets that have numerous tweets in text field
			nwords = len(tweet_separated)
			new_line_in_text = '\n' in tweet['text']
			if (len(tweet_separated) > 280) or (new_line_in_text) :
				a = 1
				new_tweets = " ".join(tweet_separated)
				new_tweets1 = new_tweets.split('\n')
				tweet_list[index]['text'] = new_tweets1[0]
				for new_tweet in new_tweets1[1:]:
					tweet_separated1 = new_tweet.split(" ")
					tweet_separated1 = clean_characters(tweet_separated1)
					header_labels = ['source', 'text', 'created_at', 'retweet_count', 'favorite_count', 'is_retweet', 'id_str', 'length']
					tweet_dict = dict()
					tweet_joined = " ".join(tweet_separated1).split(',')
					for index, label in enumerate(header_labels):

						if label == 'length':
							try:
								tweet_dict[header_labels[index]] = tweet_joined[index]
							except IndexError:
								tweet_dict[header_labels[index]] = len(tweet['text'])
						else:

							try:
								tweet_dict[header_labels[index]] = tweet_joined[index]
							except IndexError:
								tweet_dict[header_labels[index]] = None
					tweet_list.append(tweet_dict)
					a = 1
			else:
				tweet_list[index]['text'] = " ".join(tweet_separated)

	return remove_retweets(tweet_list)



def clean_characters(tweet_separated):
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
	return tweet_separated



def remove_retweets(tweet_list: list):
	''' remove rewtweets. We want Trump's tweets only '''	

	new_tweet_list = []

	for tweet in tweet_list:
		if tweet['is_retweet'] == 'false':
			new_tweet_list.append(tweet)



	return get_tweet_sentiment(new_tweet_list)



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
			tweet['grade_level'] = min(max(textstat.flesch_kincaid_grade(tweet['text']), 1), 12)
		except TypeError:
			# Tweets with no text won't be analyzed
			pass

	return assign_subject_label(tweet_list)



# def assign_subject_label(tweet_list: list):
# 	''' assign a subject label if applicable '''

# 	# Add other keywords (all lowercase) to these lists to classify tweets 
# 	# Don't add other lists without restructuring the csv writer functions  
# 	economy = ['economy', 'jobs', 'tax', 'taxes', 'gdp', 'trade', 'deficit', 'debt', 'business']
# 	covid = ['covid', 'covid-19', 'coronavirus', 'virus']
# 	foreign_policy = ['china', 'eu', 'mexico', 'canada', 'trade', 'korea', 'nafta', 'usmca', 'border', 'immigration', 'military', 'war', 'asia', 'isis']
# 	domestic_policy = ['obamacare', 'tax', 'taxes', 'immigration', 'immigrants', 'congress', 'republican', 'republicans', 'democrat', 'democrats', 'crime', 'border', 'amendment', 'military', 'healthcare', 'election', 'vote']
# 	impeachment = ['mueller', 'comey', 'witch', 'dossier', 'hoax', 'impeachment']


# 	for index, tweet in enumerate(tweet_list):
# 		if tweet['text'] != None:
# 			counter = 0
# 			tweet_words = tweet['text'].lower().split(" ")
# 			tweet['economy'] = 0
# 			tweet['covid'] = 0
# 			tweet['foreign_policy'] = 0
# 			tweet['domestic_policy'] = 0
# 			tweet['impeachment'] = 0
# 			tweet['other'] = 1

# 			for word in tweet_words:
# 				if word in economy:
# 					tweet['economy'] = 1
# 					counter += 1
# 				if word in covid:
# 					tweet['covid'] = 1
# 					counter += 1
# 				if word in foreign_policy:
# 					tweet['foreign_policy'] = 1
# 					counter += 1
# 				if word in domestic_policy:
# 					tweet['domestic_policy'] = 1
# 					counter += 1
# 				if word in impeachment:
# 					tweet['impeachment'] = 1
# 					counter += 1
# 				if counter != 0:
# 					tweet['other'] = 0

# 	return tweet_list



def assign_subject_label(tweet_list: list):
	''' Use trained Naive-Bayes Classifiers to assign tweet labels '''

	# Load classifiers and vectorizer from storage
	covid_classifier = classify.load_model("covid")
	economy_classifier = classify.load_model("economy")
	foreign_policy_classifier = classify.load_model("foreign_policy")
	domestic_policy_classifier = classify.load_model("domestic_policy")
	impeachment_classifier = classify.load_model("impeachment")
	vectorizer = classify.load_model("vectorizer")

	# prepare the tweet data and vectorize it
	all_text_only = [tweet['text'] for tweet in tweet_list]
	vectors = vectorizer.transform(all_text_only)

	# predict probabilities 
	economy_probs = classify.predict_prob(economy_classifier, vectors)
	covid_probs = classify.predict_prob(covid_classifier, vectors)
	foreign_probs = classify.predict_prob(foreign_policy_classifier, vectors)
	domestic_probs = classify.predict_prob(domestic_policy_classifier, vectors)
	impeachment_probs = classify.predict_prob(impeachment_classifier, vectors)

	# define the threshold for the classifier to assign a label 
	threshold = 0.9 

	# keep track of labels. if 0, then tweet is other
	counter = 0
	for index, tweet in enumerate(tweet_list):

		# initialize values 
		if tweet['text'] != None:
			counter = 0
			tweet['economy'] = 0
			tweet['covid'] = 0
			tweet['foreign_policy'] = 0
			tweet['domestic_policy'] = 0
			tweet['impeachment'] = 0
			tweet['other'] = 1

			# update values if the classifier says so. it is the master after all. 
			if economy_probs[index][1] > threshold:
				tweet['economy'] = 1
				counter += 1

			# only difference is covid tweets can't exist before covid-19, so ~1/1/2020
			if covid_probs[index][1] > threshold:
				if datetime.strptime(tweet['created_at'], "%m-%d-%Y %H:%M:%S") >= datetime.strptime("1 1 2020", "%m %d %Y"):
					tweet['covid'] = 1
					counter += 1
			if foreign_probs[index][1] > threshold:
				tweet['foreign_policy'] = 1
				counter += 1
			if domestic_probs[index][1] > threshold:
				tweet['domestic_policy'] = 1
				counter += 1
			if impeachment_probs[index][1] > threshold:
				tweet['impeachment'] = 1
				counter += 1
				
			if counter != 0:
				tweet['other'] = 0

	return tweet_list




def increment(count, old, new):
	''' function to increment averages by new data '''

	return (count * old + new) / (count + 1)



def group_tweets_by_month(tweet_list: list):
	''' aggregate tweetlist, group by month '''

	aggregated = dict()

	for tweet in tweet_list:
		try: 
			date = tweet['created_at'].split(" ")[0].split("-")

			try:
				month = f'{date[2]}-{date[0]}'
				data = aggregated[month] 

				new_subj = increment(data['count'], data['subjectivity'], tweet['subjectivity'])
				new_sent = increment(data['count'], data['sentiment'], tweet['sentiment'])
				new_reading = increment(data['count'], data['reading_ease'], tweet['reading_ease'])
				new_grade = increment(data['count'], data['grade_level'], tweet['grade_level'])
				new_retweet_ct = increment(data['count'], data['retweet_count'], int(tweet['retweet_count']))
				new_favorite_ct = increment(data['count'], data['favorite_count'], int(tweet['favorite_count']))
				new_length = increment(data['count'], data['length'], int(tweet['length']))

				data['count'] += 1
				data['subjectivity'] = new_subj
				data['sentiment'] = new_sent
				data['reading_ease'] = new_reading
				data['grade_level'] = new_grade
				data['retweet_count'] = new_retweet_ct
				data['favorite_count'] = new_favorite_ct
				data['length'] = new_length
				data['subject'] = 'all'

				aggregated[month] = data
			except KeyError:
				# Using this catch to add new objects to the dictionary
				aggregated[month] = {
					'count': 1, 
					'sentiment': float(tweet['sentiment']), 
					'subjectivity': float(tweet['subjectivity']),
					'reading_ease': float(tweet['reading_ease']), 
					'grade_level': float(tweet['grade_level']),
					'retweet_count': int(tweet['retweet_count']),
					'favorite_count': int(tweet['favorite_count']),
					'length': int(tweet['length']),
					'subject': 'all'
				}
			except IndexError:
				# Tweets with improperly formatted dates won't be aggregated 
				pass

		except AttributeError:
			# Tweets with no date won't be aggregated 
			pass

	return aggregated



def group_tweets_by_subject(tweet_list: list, subject):
	''' aggregate tweet_list, group by subject ''' 

	aggregated = dict()

	for tweet in tweet_list:
		if tweet[subject] == 0:
			pass
		else:
			try: 
				date = tweet['created_at'].split(" ")[0].split("-")

				try:
					month = f'{date[2]}-{date[0]}'
					data = aggregated[month] 

					new_subj = increment(data['count'], data['subjectivity'], tweet['subjectivity'])
					new_sent = increment(data['count'], data['sentiment'], tweet['sentiment'])
					new_reading = increment(data['count'], data['reading_ease'], tweet['reading_ease'])
					new_grade = increment(data['count'], data['grade_level'], tweet['grade_level'])
					new_retweet_ct = increment(data['count'], data['retweet_count'], int(tweet['retweet_count']))
					new_favorite_ct = increment(data['count'], data['favorite_count'], int(tweet['favorite_count']))
					new_length = increment(data['count'], data['length'], int(tweet['length']))

					data['count'] += 1
					data['subjectivity'] = new_subj
					data['sentiment'] = new_sent
					data['reading_ease'] = new_reading
					data['grade_level'] = new_grade
					data['retweet_count'] = new_retweet_ct
					data['favorite_count'] = new_favorite_ct
					data['length'] = new_length

					aggregated[month] = data
				except KeyError:
					# Using this catch to add new objects to the dictionary
					aggregated[month] = {
						'count': 1, 
						'sentiment': float(tweet['sentiment']), 
						'subjectivity': float(tweet['subjectivity']),
						'reading_ease': float(tweet['reading_ease']), 
						'grade_level': float(tweet['grade_level']),
						'retweet_count': int(tweet['retweet_count']),
						'favorite_count': int(tweet['favorite_count']),
						'length': int(tweet['length']),
						'subject': subject
					}
				except IndexError:
					# Tweets with improperly formatted dates won't be aggregated 
					pass

			except AttributeError:
				# Tweets with no date won't be aggregated 
				pass

	return aggregated


def add_subject_aggregates(tweet_list: list): 
	''' actually pass the subject lables to the aggregate function ''' 

	results = []
	subjects = ['economy', 'covid', 'foreign_policy', 'domestic_policy', 'impeachment', 'other']

	for subject in subjects:
		results.append(group_tweets_by_subject(tweet_list, subject))

	return results


def write_aggregated_csv(aggregated_month: dict, aggregated_subject: dict, filename: str):
	''' update a csv with aggregated data ''' 

	csv_columns = ['month', 'count', 'sentiment', 'subjectivity', 'reading_ease', 'grade_level', 'retweet_count', 'favorite_count', 'length', 'subject']

	try:
		with open(filename, 'w', newline='') as f:
			csv_writer = csv.writer(f, delimiter=",")
			csv_writer.writerow(csv_columns)
			
			for data in aggregated_month:
				values = list(aggregated_month[data].values())
				values.insert(0, data)
				
				csv_writer.writerow(values)

			for subject in aggregated_subject:
				for data in subject: 
					values = list(subject[data].values())
					values.insert(0, data)
					
					csv_writer.writerow(values)


	except IOError:
		print("IOError")

	return 




def write_data_csv(tweet_list: list, filename): 

	csv_columns = ['created_at', 'text', 'id_str', 'favorite_count', 'retweet_count', 'sentiment', 'subjectivity', 'reading_ease', 'grade_level', 'length', 'economy', 'covid', 'foreign_policy', 'domestic_policy', 'impeachment', 'other']

	try:
		with open(filename, 'w', newline='') as f:
			csv_writer = csv.writer(f, delimiter=",")
			csv_writer.writerow(csv_columns)
			
			for tweet in tweet_list:
				values = []
				for column in csv_columns:
					try:
						values.append(tweet[column])
					except KeyError:
						values.append(None)


				
				csv_writer.writerow(values)


	except IOError:
		print("IOError")

	return 


def add_subject_aggregates_day(tweet_list: list): 
	''' actually pass the subject lables to the aggregate function ''' 

	results = []
	subjects = ['economy', 'covid', 'foreign_policy', 'domestic_policy', 'impeachment', 'other']

	for subject in subjects:
		results.append(group_tweets_by_subject_day(tweet_list, subject))

	return results


def group_tweets_by_day(tweet_list: list):

	aggregated = dict()

	for tweet in tweet_list:
		try: 
			date = tweet['created_at'].split(" ")[0].split("-")

			if date[2] == '2020':

				try:
					day = f'{date[0]}-{date[1]}'
					data = aggregated[day] 

					new_subj = increment(data['count'], data['subjectivity'], tweet['subjectivity'])
					new_sent = increment(data['count'], data['sentiment'], tweet['sentiment'])
					new_reading = increment(data['count'], data['reading_ease'], tweet['reading_ease'])
					new_grade = increment(data['count'], data['grade_level'], tweet['grade_level'])
					new_retweet_ct = increment(data['count'], data['retweet_count'], int(tweet['retweet_count']))
					new_favorite_ct = increment(data['count'], data['favorite_count'], int(tweet['favorite_count']))
					new_length = increment(data['count'], data['length'], int(tweet['length']))

					data['count'] += 1
					data['subjectivity'] = new_subj
					data['sentiment'] = new_sent
					data['reading_ease'] = new_reading
					data['grade_level'] = new_grade
					data['retweet_count'] = new_retweet_ct
					data['favorite_count'] = new_favorite_ct
					data['length'] = new_length
					data['subject'] = 'all'

					aggregated[day] = data
				except KeyError:
					# Using this catch to add new objects to the dictionary
					aggregated[day] = {
						'count': 1, 
						'sentiment': float(tweet['sentiment']), 
						'subjectivity': float(tweet['subjectivity']),
						'reading_ease': float(tweet['reading_ease']), 
						'grade_level': float(tweet['grade_level']),
						'retweet_count': int(tweet['retweet_count']),
						'favorite_count': int(tweet['favorite_count']),
						'length': int(tweet['length']),
						'subject': 'all'
					}
				except IndexError:
					# Tweets with improperly formatted dates won't be aggregated 
					pass

		except AttributeError:
			# Tweets with no date won't be aggregated 
			pass

	return aggregated

def group_tweets_by_subject_day(tweet_list: list, subject):
	''' aggregate tweet_list, group by subject ''' 

	aggregated = dict()

	for tweet in tweet_list:
		if tweet[subject] == 0:
			pass
		else:
			try: 
				date = tweet['created_at'].split(" ")[0].split("-")

				if date[2] == '2020':

					try:
						day = f'{date[0]}-{date[1]}'
						data = aggregated[day] 

						new_subj = increment(data['count'], data['subjectivity'], tweet['subjectivity'])
						new_sent = increment(data['count'], data['sentiment'], tweet['sentiment'])
						new_reading = increment(data['count'], data['reading_ease'], tweet['reading_ease'])
						new_grade = increment(data['count'], data['grade_level'], tweet['grade_level'])
						new_retweet_ct = increment(data['count'], data['retweet_count'], int(tweet['retweet_count']))
						new_favorite_ct = increment(data['count'], data['favorite_count'], int(tweet['favorite_count']))
						new_length = increment(data['count'], data['length'], int(tweet['length']))

						data['count'] += 1
						data['subjectivity'] = new_subj
						data['sentiment'] = new_sent
						data['reading_ease'] = new_reading
						data['grade_level'] = new_grade
						data['retweet_count'] = new_retweet_ct
						data['favorite_count'] = new_favorite_ct
						data['length'] = new_length

						aggregated[day] = data
					except KeyError:
						# Using this catch to add new objects to the dictionary
						aggregated[day] = {
							'count': 1, 
							'sentiment': float(tweet['sentiment']), 
							'subjectivity': float(tweet['subjectivity']),
							'reading_ease': float(tweet['reading_ease']), 
							'grade_level': float(tweet['grade_level']),
							'retweet_count': int(tweet['retweet_count']),
							'favorite_count': int(tweet['favorite_count']),
							'length': int(tweet['length']),
							'subject': subject
						}
					except IndexError:
						# Tweets with improperly formatted dates won't be aggregated 
						pass

			except AttributeError:
				# Tweets with no date won't be aggregated 
				pass

	return aggregated


def write_calendar_csv(aggregated_day: dict, aggregated_subject: dict, filename: str):
	''' update a csv with aggregated data ''' 

	csv_columns = ['day', 'count', 'sentiment', 'subjectivity', 'reading_ease', 'grade_level', 'retweet_count', 'favorite_count', 'length', 'subject']

	try:
		with open(filename, 'w', newline='') as f:
			csv_writer = csv.writer(f, delimiter=",")
			csv_writer.writerow(csv_columns)
			
			for data in aggregated_day:
				values = list(aggregated_day[data].values())
				values.insert(0, data)
				
				csv_writer.writerow(values)

			for subject in aggregated_subject:
				for data in subject: 
					values = list(subject[data].values())
					values.insert(0, data)
					
					csv_writer.writerow(values)


	except IOError:
		print("IOError")

	return 




def get_most_common_words(tweet_list: list, n: int):
	''' get the list of n most common words trump tweets '''

	all_words = []

	# don't want to count articles, prepositions, etc 
	non_words = ['the', 'a', 'an',  'to', 'in', 'into', 'on', 'onto', 'at', 'for', 'by', 'and', 'or', 'is', 'are', 'am', 'were', 'was', 'of']

	for tweet in tweet_list:
		for word in tweet['text'].lower().split(" "):
			if word in non_words:
				pass
			else:
				all_words.append(word)

	return {x: count for x, count in Counter(all_words).items() if count >= n}




def get_bad_tweets(tweet_list: list): 
	''' save bad tweets to try to figure out where they are coming from ''' 

	fieldnames = tweet_list[0].keys()

	with open('bad_tweets.csv', 'w', newline='') as f:

		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()

		for tweet in tweet_list:
			if len(tweet['text']) > 280:
				writer.writerow(tweet)

	return 







if __name__ == '__main__':
	tweet_list = read_csv('tweets.csv')

	aggregated_month = group_tweets_by_month(tweet_list)
	aggregated_subject = add_subject_aggregates(tweet_list)
	write_aggregated_csv(aggregated_month, aggregated_subject, 'new_data/aggregated_tweets.csv')
	write_data_csv(tweet_list, 'new_data/tweet_data.csv')


	aggregated_day = group_tweets_by_day(tweet_list)
	aggregated_subject_day = add_subject_aggregates_day(tweet_list)
	write_calendar_csv(aggregated_day, aggregated_subject_day, 'new_data/calendar_tweets.csv')
	



	pass

	
