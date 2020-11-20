import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import gensim
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
from collections import Counter
from wordcloud import WordCloud, get_single_color_func

SUBJECTS = ["economy", "covid", "foreign_policy", "domestic_policy", "impeachment", "other"]

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)





# For coloring
# Source https://amueller.github.io/word_cloud/auto_examples/colored_by_group.html

class GroupedColorFunc(object):
    """Create a color function object which assigns DIFFERENT SHADES of
       specified colors to certain words based on the color to words mapping.

       Uses wordcloud.get_single_color_func

       Parameters
       ----------
       color_to_words : dict(str -> list(str))
         A dictionary that maps a color to the list of words.

       default_color : str
         Color that will be assigned to a word that's not a member
         of any value from color_to_words.
    """

    def __init__(self, color_to_words, default_color):
        self.color_func_to_words = [
            (get_single_color_func(color), set(words))
            for (color, words) in color_to_words.items()]

        self.default_color_func = get_single_color_func(default_color)

    def get_color_func(self, word):
        """Returns a single_color_func associated with the word"""
        try:
            color_func = next(
                color_func for (color_func, words) in self.color_func_to_words
                if word in words)
        except StopIteration:
            color_func = self.default_color_func

        return color_func

    def __call__(self, word, **kwargs):
        return self.get_color_func(word)(word, **kwargs)

# End coloring




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
    stop_words.extend(['from', 'https', 'twitter', 'twitt', 'cont', 'tinyurl', 'http', 'pqpvfm' ])
    return [[word for word in simple_preprocess(str(tweet)) if word not in stop_words] for tweet in tweets]

def rejoin_words(row):
    words = row['tokens_no_stop']
    joined_words = (" ".join(words))
    return joined_words


def create_cloud(df, filename):
    all_words = ' '.join([text for text in df.apply(rejoin_words, axis=1)])

    # Word counts - not used but could be used for d3
    # tokens = all_words.split()
    # counts = Counter(tokens)

    wordcloud = WordCloud(width=940, height=500, random_state=21, max_font_size=110, background_color='white',
                          max_words=100, normalize_plurals=False).generate(all_words)

    # Top 100 words' data means for coloring
    default_color = 'grey'
    sentiment, subjectivity, grade_level = {}, {}, {}

    for key in wordcloud.words_.keys():
        key_df = df[df['tidy_tweet'].str.contains(key)]
        sentiment[key] = key_df['sentiment'].mean()
        subjectivity[key] = key_df['subjectivity'].mean()
        grade_level[key] = key_df['grade_level'].mean()

    # Each word will go into one of these color bins - sentiment first
    colors_sentiment = ['#6f559e', '#b5afd3', '#f3eeea', '#fabb6c', '#ce7211']
    color_to_words_sentiment = {
        '#6f559e': [],
        '#b5afd3': [],
        '#f3eeea': [],
        '#fabb6c': [],
        '#ce7211': [],
    }

    lower_cutoff = -0.2
    upper_cutoff = 0.6

    sentiment_cutoffs = np.arange(lower_cutoff, upper_cutoff, ((upper_cutoff - lower_cutoff) / 5))

    for key in sentiment.keys():
        color_index = np.digitize(sentiment[key], sentiment_cutoffs)
        color_index = min(color_index, len(sentiment_cutoffs) - 1)  # keep the value in range
        # print(key, sentiment[key])
        color_to_words_sentiment[colors_sentiment[color_index]].append(key)


    # Create a color function with multiple tones
    grouped_color_func = GroupedColorFunc(color_to_words_sentiment, default_color)

    # Apply our color function
    wordcloud.recolor(color_func=grouped_color_func)

    # Show and save figure
    plt.figure(figsize=(9.4, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f"./static/{filename}_sentiment.png")
    plt.show()


    # Repeat for subjectivity
    colors_subjectivity = ['#8e0152', '#ea9ec9', '#f7f1f1', '#c1e497', '#67a833']
    color_to_words_subjectivity = {
        '#8e0152': [],
        '#ea9ec9': [],
        '#f7f1f1': [],
        '#c1e497': [],
        '#67a833': [],
    }

    lower_cutoff = 0.1
    upper_cutoff = 0.9

    subjectivity_cutoffs = np.arange(lower_cutoff, upper_cutoff, ((upper_cutoff - lower_cutoff) / 5))

    for key in subjectivity.keys():
        color_index = np.digitize(subjectivity[key], subjectivity_cutoffs)
        color_index = min(color_index, len(subjectivity_cutoffs) - 1) # keep the value in range
        # print(key, subjectivity[key])
        color_to_words_subjectivity[colors_subjectivity[color_index]].append(key)


    # Show and save figure
    grouped_color_func = GroupedColorFunc(color_to_words_subjectivity, default_color)
    wordcloud.recolor(color_func=grouped_color_func)

    plt.figure(figsize=(9.4, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f"./static/{filename}_subjectivity.png")
    plt.show()


    # Repeat for grade level (reading level)
    colors_grade_level = ['#f7fbff', '#f7fbff', '#b5d4e9', '#3c8bc2', '#08306b']
    color_to_words_grade_level = {
        '#f7fbff': [],
        '#f7fbff': [],
        '#b5d4e9': [],
        '#3c8bc2': [],
        '#08306b': [],
    }

    lower_cutoff = 1
    upper_cutoff = 12

    grade_level_cutoffs = np.arange(lower_cutoff, upper_cutoff, ((upper_cutoff - lower_cutoff) / 5))

    for key in grade_level.keys():
        color_index = np.digitize(grade_level[key], grade_level_cutoffs)
        color_index = min(color_index, len(grade_level_cutoffs) - 1) # keep the value in range
        # print(key, grade_level_cutoffs[key])
        color_to_words_grade_level[colors_grade_level[color_index]].append(key)

    # Show and save figure
    grouped_color_func = GroupedColorFunc(color_to_words_grade_level, default_color)
    wordcloud.recolor(color_func=grouped_color_func)

    plt.figure(figsize=(9.4, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f"./static/{filename}_grade_level.png")
    plt.show()


if __name__ == "__main__":


    # Read csv into dataframe
    df = pd.read_csv('tweets.csv', quotechar='', quoting=3).dropna()
    df_subjects = pd.read_csv('new_data/tweet_data.csv')

    # Convert data types and merge dataframes
    df['id_str'] = df['id_str'].apply(float)
    df['retweet_count'] = df['retweet_count'].apply(int)
    df_subjects['id_str'] = df_subjects['id_str'].apply(float)
    df = pd.merge(df, df_subjects, on='id_str', suffixes=("", "_y"))

    # Save for analyze.py potential fix
    # df.to_csv('test_file0.csv', index=False, columns=['source', 'text', 'created_at', 'retweet_count', 'favorite_count', 'is_retweet', 'id_str'])




    # Convert datatypes, drop duplicate tweets
    df['id_str'] = df['id_str'].apply(float)
    df['text'] = df['text'].apply(str)
    df['created_at'] = df['created_at'].apply(str)
    df.drop_duplicates(subset=['text'], keep='first', inplace=True)

    # Get year column
    df['year'] = df['created_at'].str.split(' ').str[0].str[-4:]

    # Remove Twitter handles and lowercase all words
    df['tidy_tweet'] = np.vectorize(remove_users)(df['text'], "@ [\w]*", "@[\w]*")
    df['tidy_tweet'] = df['tidy_tweet'].str.lower()

    # Remove hashtags
    # df['tidy_tweet'] = np.vectorize(remove_hashtags)(df['tidy_tweet'], "# [\w]*", "#[\w]*")

    # Remove links
    df['tidy_tweet'] = np.vectorize(remove_links)(df['tidy_tweet'])

    # Remove punctuation, numbers, and special characters
    df['tidy_tweet'] = df['tidy_tweet'].str.replace("[^a-zA-Z#]", " ")

    # Remove short words (length 3 and below)
    df['tidy_tweet'] = df['tidy_tweet'].apply(lambda x: ' '.join([w for w in x.split() if len(w) > 3]))

    # Remove rows with empty tweets
    df = df[df['tidy_tweet'].astype(bool)]

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
