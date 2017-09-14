
# coding: utf-8

# In[1]:


from tweepy import API, OAuthHandler
from data_analysis.database import session, Tweet


# In[2]:


consumer_key='Y9G7gt9pNcV3Z0svkMx5Z1Pjz'
consumer_secret='p0Bwe8uXRDhn5plqph66ftSzEdRMMcoFvUNJkJxFy1TIkXC1cZ'
access_token='601123109-vK3Wgh9GreRd5vIbA5CugfaMrC9Yp5PGJHkXmmnT'
access_token_secret='GNrlkhtFDAMK4zJw1cJmotmq1GlF2GUihPSMnq4h8Tai5'


# In[3]:


auth = OAuthHandler(consumer_key=consumer_key, consumer_secret=consumer_secret)

auth.set_access_token(access_token, access_token_secret)


# In[4]:


def update_tweets(api, tweets):
    """
    A method to update our tweets
    `api`    - an instance of tweepy.API
    `tweets` - a list of tweets from the database
    
    """
    # Number of tweets
    len_tweets = len(tweets)
    
    # Tweepy Rest API takes only 100 id's at once
    block_size=100
    
    for it in range(0, len_tweets, block_size):
        st_index = it
        end_index = it + block_size
        _update_block(api, session, tweets[st_index:end_index])
        print("Updated {} tweets".format(end_index))


# In[5]:
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

def _update_block(api, session, tweets):
    """
    Helper method for updating a block of tweets
    """
    # Grab ids from the given block of tweets
    tweet_ids = [tweet.tid for tweet in tweets]
    
    # Grab the updated tweets using api lookup
    updated_tweets = api.statuses_lookup(tweet_ids, trim_user=True)
    # `trim_user` drops the user data
    
    # Iterate over all the updated tweets
    for updated_tweet in updated_tweets:
        try: 
            # Get the database tweet
            db_tweet = session.query(Tweet).filter_by(tid=updated_tweet.id).one()
            
            # update the details
            db_tweet.favorite_count, db_tweet.retweet_count = updated_tweet.favorite_count, updated_tweet.retweet_count
        except MultipleResultsFound as e:
            print('MultipleResultsFound: {}'.format(e))
        except NoResultFound as e:
            print('NoResultFound: {}'.format(e))

    # commit changes to the database
    session.commit()


# In[6]:


def main():
    api = API(auth)
    
    # Get all the tweets
    tweets = session.query(Tweet).all()
    update_tweets(api, tweets)

    print("Updated all tweets")
if __name__ == "__main__":
    main()

