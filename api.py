# This file handles the basic data read operations from the csv files in the project folder

# import the necessary libraries
import csv 

def get_csv_data(path_to_file):
	''' main function to load csv data into a dict''' 

	data_list = []

	with open(path_to_file, 'r') as f:
		csv_reader = csv.reader(f, delimiter=',')
		header_labels = list(next(csv_reader))

		for row in csv_reader:
			data = dict()
			for index, label in enumerate(header_labels):
				try:
					data[header_labels[index]] = row[index]
				except IndexError:
					data[header_labels[index]] = None
			data_list.append(data)

	return data_list




def get_aggregated_tweets():
	''' get the current version of the aggregated tweets to display '''

	return get_csv_data('new_data/aggregated_tweets.csv')



def get_tweet_data():
	''' get the current tweet data to display '''

	return get_csv_data('new_data/tweet_data.csv')



def get_events(): 
	''' get the current event data to display ''' 

	return get_csv_data('new_data/events.csv')


def get_calendar():
	''' get the calendar data to display ''' 

	return get_csv_data('new_data/calendar_tweets.csv')







