from difflib import SequenceMatcher

import tweepy
import re

# Consumer keys and access tokens, used for OAuth
consumer_key = 'kBVZd9svwvJap0gHzJ1czYFpa'
consumer_secret = '4J4xGV4QU8xTdr8TnfwLUXpcu7w54GtazglN31PIB9uK20yM1S'
access_token = '798279989573586947-KpVsmDmSSEL3hT0K5iFzCvkisgGQoxY'
access_token_secret = 'mOn1xNThq41ALg9yk4xctNb3q8q9EPPnIAzPYSs9H486g'

wordList = ['απο', 'και', 'είναι', 'είμαι', 'εσεις', 'εμεις', 'τον', 'την']
 
# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
 
# Creation of the actual interface, using authentication
api = tweepy.API(auth)


class MyStreamListener(tweepy.StreamListener):
    '''Dealing with the tweets. Checking if they are valid for RT'''
    hasMention = re.compile(r"\@")
    hasURL = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    tweet_list = []

    def is_similar(self, tweet):
        ratio = SequenceMatcher(None, tweet, self.tweet_list[0]).ratio()
        # print('ratio for ~~'+ tweet +'~~   = ' + str(ratio))
        return ratio

    def number_of_hashtags(self, tweet):
        return len(re.findall(r"#", tweet))

    def is_valid(self, tweet):
        tweet_array = tweet.split()
        return bool(self.hasMention.search(tweet) is None and
                    self.hasURL.search(tweet) is None and
                    len(tweet_array) < 10 and len(tweet_array) > 2 and
                    self.number_of_hashtags(tweet) < 2)

    def on_status(self, status):
        if self.is_valid(status.text):
            print(status.text)

        if not self.tweet_list:
            self.tweet_list.append(status.text)
        else:
            if self.is_similar(status.text) > 0.6: #change that to < 0.6
                self.tweet_list.append(status.text)
        self.retweet()

    def retweet(self):
        if self.tweet_list == 2:
            print('we have a match!!')
            print(self.tweet_list[0])
            print(self.tweet_list[1])
            self.tweet_list = []

myStreamListener = MyStreamListener()
tweet_stream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
tweet_stream.filter(track=wordList)
