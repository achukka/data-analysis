import json
from os import path

from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener

from sqlalchemy.orm.exc import NoResultFound

from data_analysis.database import session, Tweet, Hashtag, User

consumer_key='Y9G7gt9pNcV3Z0svkMx5Z1Pjz'
consumer_secret='p0Bwe8uXRDhn5plqph66ftSzEdRMMcoFvUNJkJxFy1TIkXC1cZ'
access_token='601123109-vK3Wgh9GreRd5vIbA5CugfaMrC9Yp5PGJHkXmmnT'
access_token_secret='GNrlkhtFDAMK4zJw1cJmotmq1GlF2GUihPSMnq4h8Tai5'

auth = OAuthHandler(consumer_key,
					consumer_secret)

auth.set_access_token(access_token, access_token_secret)


# Save Tweets to Database
def save_tweets():
	directory = _get_directory_absolute_path()
	filepath = path.join(directory, 'tweets.json')

	# Create a listener for the database
	listener = DatabaseListener(number_tweets_to_save=1000,
								filepath=filepath)
	# Create a stream using the listener
	stream = Steam(auth, listener)
	languages = ('en',)

	try:
		# Now sample tweets belonging to the given languages from the stream
		stream.sample(languages=languages)
	except KeyboardInterrupt:
		listener.file.close()


class DatabaseListener(StreamListener):
	def __init__(self, number_tweets_to_save, filepath=None):
		self._final_count = number_tweets_to_save
		self._current_count = 0
		if filepath is None:
			filepath = 'tweets.txt'
		self.file = open(filepath, w)

	# Note: Slightly dangerous due to circular references
	def _del(self):
		self.file.close()

	def on_data(self, raw_data):
		data = json.loads(raw_data)
		json.dump(raw_data, self.file)
		self.file.write('\n')
		if "in_reply_to_status_id" in data:
			return self.on_status(data)

	def on_status(self, data):
		# Note: This method is defined in this file
		save_to_database(data)

		self._current_count += 1
		print("Status count: {}".format(self._current_count))
		if self._current_count >= self._final_count:
			return False

# Helper method to create an 'user' using json data
def create_user_helper(user_data):
	user = User(uid=user_data['id_str'], 
				name=user_data['name'], 
				screen_name=user_data['screen_name'], 
				created_at=user_data['created_at'], 
				description=user_data.get('description'), 
				followers_count=user_data['followers_count'], 
				statuses_count=user_data['user_data'], 
				favorites_count=user_data['favorites_count'], 
				listed_count=user_data['listed_count'], 
				geo_enabled=user_data['geo_enabled'], 
				lang=user_data.get('lang'))
	return user

# Helper method to create a 'tweet' using json data
def create_tweet_helper(tweet_data, user):
	retweet = True if tweet_data['text'][:3] == 'RT' else False
	coordinates = json.dumps(tweet_data['coordinates'])
	tweet = Tweet(tid=tweet_data['id_str'], 
				  tweet=tweet_data['text'], 
				  user=user, 
				  coordinates=coordinates, 
				  created_at=tweet_data['created_at'], 
				  favorite_count=tweet_data['favorite_count'], 
				  in_reply_to_screen_name=tweet_data['in_reply_to_screen_name'], 
				  in_reply_to_status_id=tweet_data['in_reply_to_status_id'], 
				  in_reply_to_user_id=tweet_data['in_reply_to_user_id'], 
				  lang=tweet_data.get('lang'), 
				  quoted_status_id=tweet_data.get('quoted_status_id'), 
				  retweet_count=tweet_data['retweet_count'], 
				  source=tweet_data['source'], 
				  is_retweet=retweet)
	return tweet

# Save the objects to the database
def save_to_database(data):
	try:
		user = session.query("User").filter_by(id=str(data["user"]["id"])).one()
	except NoResultFound:
		user = create_user_helper(data['user'])
		session.add(user)

	hashtag_results = []
	hashtags = data['entities']['hashtags']
	for hashtag in hashtags:
		hashtag = hashtag['text'].lower()
		try:
			hashtag = session.query("Hashtag").filter_by(text=hashtag).one()
		except NoResultFound:
			hashtag_obj = Hashtag(text=hashtag)
			session.add(hashtag_obj)
		hashtag_results.append(hashtag_obj)
	
	# Create a tweet object from the given data and the user
	tweet = create_tweet_helper(data, user)
	
	# Add the hashtag to the tweet
	for hashtag in hashtag_results:
		tweet.hashtags.append(hashtag)

	# Add the tweet to the current session and commit
	session.add(tweet)
	session.commit()

def _get_directory_absolute_path():
	"""
	helper method to get the absolute path of the file directory
	"""
	directory = path.abspath(path.dirname(__file__))
	return directory