from difflib import SequenceMatcher
import re
import string
import tweepy
import pyphen

WORDLIST = ['απο', 'και', 'είναι', 'είμαι', 'εσείς',
 'εμείς', 'τον', 'την', 'ο', 'η', 'το', 'που']


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
    hasURL = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    tweet_list = {}

    def is_similar(self, tweet):
        '''Checking if the two tweets in the list are similar, same or RT'''
        ratio = SequenceMatcher(None, tweet, self.tweet_list[0]).ratio()
        # print('ratio for ~~'+ tweet +'~~   = ' + str(ratio))
        return ratio

    def number_of_hashtags(self, tweet):
        '''Checking the number of hashtags in the tweet'''
        return len(re.findall(r"#", tweet))

    def is_valid(self, tweet):
        '''main function that checks the validity of the tweet. A number of
        things must happen.The tweet has to has less that 10 words, more
        than 2 words, less than 2 hashtags and doesnt have any mentions'''
        tweet_array = tweet.split()
        return bool(self.hasMention.search(tweet) is None and
                    self.hasURL.search(tweet) is None and
                    len(tweet_array) < 10 and len(tweet_array) > 2 and
                    self.number_of_hashtags(tweet) < 2)

    def is_english(self, word):
        '''Checks if the word is english'''
        try:
            word.encode('ascii')
        except UnicodeEncodeError:
            return False
        else:
            return True

    def clean_text(self, data):
        '''remove emoji from the data'''
        translator = str.maketrans({key: " " for key in string.punctuation})
        out = data.translate(translator)
        emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
        return emoji_pattern.sub('', out)

    def normalise_dic_key(self, tweet_key):
        '''Makes all Greek letters like η,ι,ει.οι and ε, αι the same
        for comparison reasons. This is used for the dictionary key'''
        out = re.sub(r"(?:αι|αί|έ)", "ε", tweet_key)
        out = re.sub(r"(?:η|ή|ει|εί|οι|οί|ί)", "ι", out)
        return out[-4:]

    def last_two_syllables(self, tweet):
        '''Returns the last 1 or 2 syllables of the last word'''
        dic = pyphen.Pyphen(lang='el_GR')

        if not self.is_english(tweet.split()[-1]):
            for_hyphenation = tweet.split()[-1]
        else:
            for_hyphenation = tweet.split()[-2]

        hyphenated = dic.inserted(for_hyphenation).split('-')
        if len(hyphenated) > 1:
            if len(hyphenated[-2]+hyphenated[-1]) < 4:
                return hyphenated[-2]+hyphenated[-1]

        return hyphenated[-1]

    def check_pair_found(self, key, data):
        '''This function checks if we have the last 4 letters already.
        if we do then it retweets the two messages. If not, adds them to
        the list for later.'''
        if key in self.tweet_list:
            self.retweet(data, self.tweet_list[key])
        self.tweet_list[key] = data

    def on_status(self, data):
        '''this is the tweepy function that runs whenever we receive a tweet'''
        status = self.clean_text(data.text)
        if self.is_valid(data.text):
            key = self.normalise_dic_key(self.last_two_syllables(status))
            self.check_pair_found(key=key, data=[data.id, status])
            # print(str(data.id) + " " + status + " LS= " + key)

    def retweet(self, tweet_array1, tweet_array2):
        '''Function for retweeting the correct tweets'''
        print("found a pair!!")
        print(tweet_array1[1])
        print(tweet_array2[1])

API = auth_with_tweeter()
MYSTREAM = MyStreamListener()
TWEET_HOSE = tweepy.Stream(auth=API.auth, listener=MYSTREAM)
TWEET_HOSE.filter(track=WORDLIST)
