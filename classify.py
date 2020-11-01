# This file implements a Naive Bayes Classifier to assign subject labels to tweets
# DVA - Fall 2020 

# import external libraries
import csv
import pandas as pd
import pickle
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB


# import files from the project root directory
import analyze



def get_training_set(tweet_list: list):
	''' all tweets that are currently labeled are going to be used as the training set ''' 

	return [tweet for tweet in tweet_list if tweet['other'] != 1]



def extract_lables(tweet_list: list, subject: str): 
	''' extract labels as a one-hot array ''' 

	labels = [0 for tweet in tweet_list]

	for index, tweet in enumerate(tweet_list):
		labels[index] += tweet[subject]

	return labels



def count_vectorize(tweet_list: list, fit: bool): 
	''' call the sklean countvectorizer function to convert word counts in a tweet to a vector ''' 

	text_only = [tweet['text'] for tweet in tweet_list]

	cv = CountVectorizer(strip_accents='ascii', token_pattern=u'(?ui)\\b\\w*[a-z]+\\w*\\b', lowercase=True, stop_words='english')
	vectors = cv.fit_transform(text_only)

	## Uncomment this to see the word frequency array and the tweets that contain them 
	# word_freq_df = pd.DataFrame(vectors.toarray(), columns=cv.get_feature_names())
	# print(word_freq_df)


	return vectors 



def train(tweet_list: list, labels: list):
	''' train an Multinomial Naive Bayes Classifier on the subject label in the training set ''' 

	vectors = count_vectorize(tweet_list)
	
	classifier = MultinomialNB()
	classifier.fit(vectors, labels)
	
	return classifier



def test(classifier, tweet_list: list, labels: list): 
	''' test the classifier on dataset '''

	vectors = count_vectorize(tweet_list)
	predicitions = classifier.predict(vectors)

	count = 0
	correct = 0
	for index, label in enumerate(labels):
		if label == predicitions[index]:
			correct += 1
		count += 1 

	return correct / count



def predict_prob(classifier, vectors: list): 
	''' predicit the probability for each label for each tweet ''' 

	return classifier.predict_proba(vectors)



def save_model(classifier, subject: str):
	''' save the parameters of the trained classifier for future use without needing to retrain ''' 

	pickle.dump(classifier, open("classifiers/" + subject + ".sav", 'wb'))



def load_model(subject: str): 
	''' load the parameters from a model that was perviously saved ''' 

	return pickle.load(open("classifiers/" + subject + ".sav", 'rb'))





def update_all_classifiers(tweet_list: list): 
	''' call this function to update all classifiers and then save them to the disk ''' 

	training_set = get_training_set(tweet_list)

	# get labels for each subject and classifier. 
	economy_labels = extract_lables(training_set, 'economy')
	covid_labels = extract_lables(training_set, 'covid')
	foreign_policy_labels = extract_lables(training_set, 'foreign_policy')
	domestic_policy_labels = extract_lables(training_set, 'domestic_policy')
	impeachment_labels = extract_lables(training_set, 'impeachment')

	# train each classifier
	economy_classifier = train(training_set, economy_labels)
	covid_classifier = train(training_set, covid_labels)
	foreign_policy_classifier = train(training_set, foreign_policy_labels)
	domestic_policy_classifier = train(training_set, domestic_policy_labels)
	impeachment_classifier = train(training_set, impeachment_labels)

	# test each classifier
	print("Training Set Accuracy - Economy: ", end = "")
	print(test(economy_classifier, training_set, economy_labels))

	print("Training Set Accuracy - Covid: ", end = "")
	print(test(covid_classifier, training_set, covid_labels))

	print("Training Set Accuracy - Foreign Policy: ", end = "")
	print(test(foreign_policy_classifier, training_set, foreign_policy_labels))

	print("Training Set Accuracy - Domestic Policy: ", end = "")
	print(test(domestic_policy_classifier, training_set, domestic_policy_labels))

	print("Training Set Accuracy - Impeachment: ", end = "")
	print(test(impeachment_classifier, training_set, impeachment_labels))

	# save classifier parameters for future use
	save_model(economy_classifier, "economy")
	save_model(covid_classifier, "covid")
	save_model(foreign_policy_classifier, "foreign_policy")
	save_model(domestic_policy_classifier, "domestic_policy")
	save_model(impeachment_classifier, "impeachment")


def plot_prob_dist(tweet_list: list): 
	''' ''' 

	economy_classifier = load_model("economy")
	covid_classifier = load_model("covid")
	foreign_policy_classifier = load_model("foreign_policy")
	domestic_policy_classifier = load_model("domestic_policy")
	impeachment_classifier = load_model("impeachment")
	vectorizer = load_model("vectorizer")

	all_text_only = [tweet['text'] for tweet in tweet_list]
	vectors = vectorizer.transform(all_text_only)

	economy_probs = predict_prob(economy_classifier, vectors)
	covid_probs = predict_prob(covid_classifier, vectors)
	foreign_probs = predict_prob(foreign_policy_classifier, vectors)
	domestic_probs = predict_prob(domestic_policy_classifier, vectors)
	impeachment_probs = predict_prob(impeachment_classifier, vectors)

	plt.hist(economy_probs[:, 1])
	plt.title("Economy")
	plt.xlabel("Tweet Probability")
	plt.savefig("figures/economy_dist")
	plt.cla()

	plt.hist(covid_probs[:, 1])
	plt.title("Covid")
	plt.xlabel("Tweet Probability")
	plt.savefig("figures/covid_dist")
	plt.cla()

	plt.hist(foreign_probs[:, 1])
	plt.title("Foreign Policy")
	plt.xlabel("Tweet Probability")
	plt.savefig("figures/foreign_policy_dist")
	plt.cla()

	plt.hist(domestic_probs[:, 1])
	plt.title("Domestic Policy")
	plt.xlabel("Tweet Probability")
	plt.savefig("figures/domestic_policy_dist")
	plt.cla()

	plt.hist(impeachment_probs[:, 1])
	plt.title("Impeachment")
	plt.xlabel("Tweet Probability")
	plt.savefig("figures/impeachment_dist")
	plt.cla()



if __name__ == '__main__':

	# get tweets and split into a training set
	# training set is all tweets that are labeled by the matching algorithm already
	tweet_list = analyze.read_csv('tweets.csv')




	pass
	













