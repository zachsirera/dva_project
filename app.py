from flask import Flask, render_template

import analyze

app = Flask(__name__)

@app.route('/')
def home():
	tweet_list = analyze.get_aggregated_tweets()
	return render_template('home.html', tweet_list=tweet_list)

if __name__ == '__main__':
	app.run()