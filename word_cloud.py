import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import gensim
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
from collections import Counter
from wordcloud import WordCloud

SUBJECTS = ["economy", "covid", "foreign_policy", "domestic_policy", "impeachment", "other"]

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


def remove_users(tweet, pattern1, pattern2):
    r = re.findall(pattern1, tweet)
    for i in r:
        tweet = re.sub(i, '', tweet)

    r = re.findall(pattern2, tweet)
    for i in r:
        tweet = re.sub(i, '', tweet)
    return tweet


def remove_hashtags(tweet, pattern1, pattern2):
    r = re.findall(pattern1, tweet)
    for i in r:
        tweet = re.sub(i, '', tweet)

    r = re.findall(pattern2, tweet)
    for i in r:
        tweet = re.sub(i, '', tweet)
    return tweet


def remove_links(tweet):
    tweet_no_link = re.sub(r"http\S+", "", tweet)
    return tweet_no_link

def tokenize(tweet):
    for word in tweet:
        yield(gensim.utils.simple_preprocess(str(word), deacc=True))  # deacc=True Removes punctuations


def remove_stopwords(tweets):
    stop_words = stopwords.words('english')
    stop_words.extend(['from', 'https', 'twitter', 'twitt', 'cont', 'tinyurl' ])
    return [[word for word in simple_preprocess(str(tweet)) if word not in stop_words] for tweet in tweets]

def rejoin_words(row):
    words = row['tokens_no_stop']
    joined_words = (" ".join(words))
    return joined_words


def create_cloud(df, filename):
    # df['no_stop_joined'] = df.apply(rejoin_words, axis=1)
    all_words = ' '.join([text for text in df.apply(rejoin_words, axis=1)])

    # Word counts - not used but could be used for d3
    tokens = all_words.split()
    counts = Counter(tokens)

    wordcloud = WordCloud(width=900, height=600, random_state=21, max_font_size=110, background_color='ghostwhite',
                          max_words=200, normalize_plurals=False).generate(all_words)

    plt.figure(figsize=(12, 8))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.savefig(f"./images/{filename}.png")
    plt.show()


if __name__ == "__main__":


    # Read csv into dataframe
    df = pd.read_csv('tweets.csv', quotechar='', quoting=3).dropna()
    df_subjects = pd.read_csv('tweet_data.csv')

    # Convert data types and merge dataframes
    df['id_str'] = df['id_str'].apply(float)
    df_subjects['id_str'] = df_subjects['id_str'].apply(float)
    df = pd.merge(df, df_subjects, on='id_str', suffixes=("", "_y"))

    # Convert datatypes, drop duplicate tweets
    df['text'] = df['text'].apply(str)
    df['created_at'] = df['created_at'].apply(str)
    df.drop_duplicates(subset=['text'], keep='first', inplace=True)

    # Get year column
    df['year'] = df['created_at'].str.split(' ').str[0].str[-4:]

    # Remove Twitter handles and lowercase all words
    df['tidy_tweet'] = np.vectorize(remove_users)(df['text'], "@ [\w]*", "@[\w]*")
    df['tidy_tweet'] = df['tidy_tweet'].str.lower()

    # Remove the retweets
    # df = df[(df['is_retweet'] == "false")]

    # Remove hashtags
    # df['tidy_tweet'] = np.vectorize(remove_hashtags)(df['tidy_tweet'], "# [\w]*", "#[\w]*")

    # Remove links
    # df['tidy_tweet'] = np.vectorize(remove_links)(df['tidy_tweet'])

    # Remove punctuation, numbers, and special characters
    df['tidy_tweet'] = df['tidy_tweet'].str.replace("[^a-zA-Z#]", " ")

    # Remove short words (length 3 and below)
    df['tidy_tweet'] = df['tidy_tweet'].apply(lambda x: ' '.join([w for w in x.split() if len(w) > 3]))

    # Tokenize words and clean-up punctuations
    df['tidy_tweet_tokens'] = list(tokenize(df['tidy_tweet']))

    # Remove stopwords
    df['tokens_no_stop'] = remove_stopwords(df['tidy_tweet_tokens'])

    # Split by year
    df_yearly_list = [pd.DataFrame(y) for x, y in df.groupby('year', as_index=False)]

    # Create a word cloud for each year
    for df_year in df_yearly_list:
        year = df_year['year'].iloc[0]
        create_cloud(df_year, year)
        for subject in SUBJECTS:
            df_current_subject = df_year[(df_year[subject] == 1)]
            # Create word cloud for the subject only if there are > 5 tweets
            if df_current_subject.shape[0] > 5:
                create_cloud(df_current_subject, f"{year}_{subject}")



# Hashtag code
# Top Hashtags dataframe
# df['hashtags'] = df['tidy_tweet'].apply(lambda twt: re.findall(r"#(\w+)", twt))
# d = Counter(df.hashtags.sum())
# df_hashtags = pd.DataFrame([d]).T
# df_hashtags.columns = ['freq']
# print(df_hashtags.freq.sum())
# df_hashtags.sort_values(by=['freq'], ascending=False, inplace=True)
# print(df_hashtags.head(20))
# Visualize it
# labels = df_hashtags.head(25).index.values.tolist()
# freq = df_hashtags['freq'].head(25).values.tolist()
# index = np.arange(len(freq))
# plt.figure(figsize=(12, 9))
# plt.bar(index, freq, alpha=0.8, color='black')
# plt.xlabel('Hashtags', fontsize=13)
# plt.ylabel('Frequency', fontsize=13)
# plt.xticks(index, labels, fontsize=11, rotation=90, fontweight="bold")
# plt.title('Top 25 Hashtags of dataset', fontsize=12, fontweight="bold")
# plt.show()
# df = df.drop(['hashtags'], axis=1)