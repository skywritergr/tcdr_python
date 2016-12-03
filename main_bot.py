from difflib import SequenceMatcher
import re
import string
import tweepy
import pyphen
import json
import pika

WORDLIST = ['Chelsea']


def auth_with_tweeter():
    '''Authenticate with twitter'''
    # Consumer keys and access tokens, used for OAuth
    consumer_key = 'kBVZd9svwvJap0gHzJ1czYFpa'
    consumer_secret = '4J4xGV4QU8xTdr8TnfwLUXpcu7w54GtazglN31PIB9uK20yM1S'
    access_token = '798279989573586947-KpVsmDmSSEL3hT0K5iFzCvkisgGQoxY'
    access_token_secret = 'mOn1xNThq41ALg9yk4xctNb3q8q9EPPnIAzPYSs9H486g'

    # OAuth process, using the keys and tokens
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Creation of the actual interface, using authentication
    api = tweepy.API(auth)

    return api


class MyStreamListener(tweepy.StreamListener):
    '''Dealing with the tweets. Checking if they are valid for RT'''
    hasMention = re.compile(r"\@")
    tweet_list = {}

    def is_similar(self, tweet):
        '''Checking if the two tweets in the list are similar, same or RT'''
        ratio = SequenceMatcher(None, tweet, self.tweet_list[0]).ratio()
        # print('ratio for ~~'+ tweet +'~~   = ' + str(ratio))
        return ratio

    def number_of_hashtags(self, tweet):
        '''Checking the number of hashtags in the tweet'''
        return len(re.findall(r"#", tweet))

    def is_english(self, word):
        '''Checks if the word is english'''
        try:
            word.encode('ascii')
        except UnicodeEncodeError:
            return False
        else:
            return True

    def on_status(self, data):
        '''this is the tweepy function that runs whenever we receive a tweet'''
        # print(str(data.id) + " " + data.text)
        print(json.dumps(data._json, indent=4))
        return False

API = auth_with_tweeter()
MYSTREAM = MyStreamListener()
TWEET_HOSE = tweepy.Stream(auth=API.auth, listener=MYSTREAM)
TWEET_HOSE.filter(track=WORDLIST)
