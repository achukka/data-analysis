from tweepy import OAuthHandler, Stream, API
from tweepy.streaming import StreamListener
import json

consumer_key='Y9G7gt9pNcV3Z0svkMx5Z1Pjz'
consumer_secret='p0Bwe8uXRDhn5plqph66ftSzEdRMMcoFvUNJkJxFy1TIkXC1cZ'
access_token='601123109-vK3Wgh9GreRd5vIbA5CugfaMrC9Yp5PGJHkXmmnT'
access_token_secret='GNrlkhtFDAMK4zJw1cJmotmq1GlF2GUihPSMnq4h8Tai5'

auth = OAuthHandler(consumer_key,
					consumer_secret)

auth.set_access_token(access_token, access_token_secret)

TWEET_THRESHOLD = -1

class PrintListener(StreamListener):
	def on_status(self, status):
		#if not status.text[:3] == 'RT':
		# Condition for Original Tweets
		print(status.text)
		print(status.author.name, status.created_at, status.source, "\n")

	def on_error(self, status_code):
		print("Error Code: {}".format(status_code))
		return True # Keeps the stream alive

	def on_timeout(self):
		print("Listener timed out!")
		return True # Keeps the stream alive


def print_to_terminal():
	print_listener = PrintListener()
	stream = Stream(auth, print_listener)
	languages = ('en', )
	stream.sample(languages=languages)

def pull_down_tweets(screen_name):
	print('Getting Tweets from: {}'.format(screen_name))
	api = API(auth)
	tweets = api.user_timeline(screen_name=screen_name, count=200)
	user = api.get_user(screen_name)
	print("Followers count : {}".format(user.followers_count))
	print("Friends count : {}".format(user.friends_count))
	print("Favorties count : {}".format(user.favourites_count))
	print("Number of tweets: {}".format(len(tweets)))
	
	for (i, tweet) in enumerate(tweets):
		if tweet.place is not None:
			place = tweet.place
			print('Id:{}, Country:{}, Code:{}, Full Name:{}, Name:{}, Place Type:{}, Tweet: {}'.
				format(i, place.country, place.country_code, 
					place.full_name, place.name, 
					place.place_type, tweet.text))
					#json.dumps(tweet._json, indent=4)))
		if tweet.retweeted:
			if tweet.retweet_count > TWEET_THRESHOLD:
				print('Id: {} Retweet Count: {}, Withhled in Countries: {}, Tweet: {}'.
					format(i, tweet.retweet_count, 
						tweet.Withhled_in_countries, tweet.text))
						#json.dumps(tweet._json, indent=4)))

if __name__ == '__main__':
	#print_to_terminal()
	# pull_down_tweets(auth.get_username())
	#pull_down_tweets('realDonaldTrump')
	pull_down_tweets('Twitter')