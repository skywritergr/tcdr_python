from flask import Flask, Response, request
import re
import tweepy
import json

app = Flask(__name__)


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

API = auth_with_tweeter()


def get_tweets_for_user(user_id):
    tweets = API.user_timeline(user_id=user_id, count=100)
    final_text = ""
    for tweet in tweets:
        tweet_text = tweet._json["text"]
        raw_text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet_text).split())
        final_text += (" " + raw_text)
    # print(final_text)
    return final_text


def get_object(data):
    final_obj = {}
    user_id = data._json["user"]["id_str"]
    # print(json.dumps(data._json, indent=4))
    final_obj["user_id"] = user_id
    final_obj["location"] = data._json["user"]["location"]
    final_obj["tweets"] = get_tweets_for_user(user_id)
    return final_obj


@app.route('/samaritans')
def users_to_help():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    users_array = []
    search_results = API.search(q="refugees", geocode=lat+","+lon+",5mi",
                                count=10)
    counter = 0
    for tweet in search_results:
        counter += 1
        obj = get_object(tweet)
        users_array.append(obj)
    # print(search_results)
    return Response(json.dumps(users_array),  mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
