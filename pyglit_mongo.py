"""
Python Geolocation Listener for Twitter
"""

import sys
import os
import json
import datetime
import re
import tweepy
import shapely.geometry as shp
import textwrap
import config
import state_geometry as sg
from pymongo import MongoClient


# ======================================================================================================================
# Main Function
# ======================================================================================================================
def main():
    client = MongoClient()
    db = client['politisent_tweets']
    collection = db[state_code]
    auth = authenticate()
    start_stream(auth, collection)
    return


# ======================================================================================================================
# Listener Class
# ======================================================================================================================
class Listener(tweepy.StreamListener):
    def __init__(self, collection, api=None):
        self.collection = collection
        self.num_tweets = 0
        self.tweet_limit = config.tweet_limit

    def on_data(self, data):
        data_string = json.loads(data)
        if config.state:
            if state_filter(data):
                self.collection.insert_one(data_string)
                self.num_tweets += 1
                print self.num_tweets
            else:
                pass
        else:
            self.collection.insert_one(data_string)
            self.num_tweets += 1
            print self.num_tweets

        # run until n tweets collected
        if self.tweet_limit and self.num_tweets > self.tweet_limit:
            print "\nLimit hit: {} tweets collected!\nExiting...\n".format(self.tweet_limit)
            clean_up()
            sys.exit()

    def on_limit(self, track):
        print 'Limit hit! Track = {}'.format(track)
        return

    def on_error(self, status_code):
        print 'An error has occured! Status code = {}'.format(status_code)
        return

    def on_timeout(self):
        print 'Timeout: Snoozing Zzzzzz'
        return


# ======================================================================================================================
# Auxilliary Functions
# ======================================================================================================================

def authenticate():
    c_tok = config.consumer_token
    c_sec = config.consumer_secret
    acc_tok = config.access_token
    acc_sec = config.access_secret

    auth = tweepy.OAuthHandler(c_tok, c_sec)
    auth.set_access_token(acc_tok, acc_sec)

    return auth


def start_stream(auth, collection="general"):
    stream = tweepy.Stream(auth, listener=Listener(collection))
    if config.state:
        bbox = sg.retrieve_bbox(config.state)
    elif config.bbox:
        bbox = config.bbox
    else:
        sys.exit("ERROR: You must specify either the state of interest or a bounding box in config.py!")
    stream.filter(locations=bbox)


def state_filter(json_obj):
    tweet = json.loads(json_obj)
    try:
        if config.state:
            try:
                name = tweet['place']['full_name']
                if name is not None:
                    if re.match(config.state, name, re.IGNORECASE) or \
                        re.match(r'.*, {}$'.format(state_code), name, re.IGNORECASE) or \
                        re.match(r'.*, {}$'.format(state_code), tweet['user']['location'], re.IGNORECASE):
                        return True
                    else:
                        return False
                elif tweet["coordinates"] is not None:
                    point = shp.Point(tweet["coordinates"]["coordinates"][1], tweet["coordinates"]["coordinates"][0])
                    if point.within(state_poly):
                        return True
                    else:
                        return False
                elif tweet["place"]["bounding_box"] is not None:
                    corners = tweet["place"]["bounding_box"]["coordinates"][0]
                    points = sg.coords2points(corners)
                    bbox = shp.MultiPoint(points).convex_hull
                    if bbox.within(state_poly):
                        return True
                    else:
                        return False
                else:
                    return False
            except TypeError:   # Type error is thrown when user location is None.
                                # User location is only checked if state-code or state name not found in full_name.
                return False
        else:
            if tweet["coordinates"] is not None:
                point = shp.Point(tweet["coordinates"]["coordinates"][1], tweet["coordinates"]["coordinates"][0])
                if point.within(state_poly):
                    return True
                else:
                    return False
            elif tweet["place"]["bounding_box"] is not None:
                corners = tweet["place"]["bounding_box"]["coordinates"][0]
                points = sg.coords2points(corners)
                bbox = shp.MultiPoint(points).convex_hull
                if bbox.within(state_poly):
                    return True
                else:
                    return False
            else:
                return False
    except KeyError:
        return False


def state_code(state):
    with open("state_codes.txt","rb") as f:
        text = f.read()
    try:
        code = re.search(r'{} = "(.*?)"'.format(state),text, re.IGNORECASE).group(1)
    except AttributeError:
        sys.exit("ERROR: wasn't able to look up the code for your state in state_codes.txt. "
                 "Are you sure you spelled it right in config.py??")
    return code


def clean_up():
    now = str(datetime.datetime.now())
    with open(os.path.join(script_dir, "output/pyglit_tweet_stream.json"), 'a') as f:
        f.write("\n\nTWITTER COLLECTION ENDED: {}".format(now))
    with open(os.path.join(script_dir, "output/pyglit_tweet_stream.txt"), 'a') as f:
        f.write("\n\nTWITTER COLLECTION ENDED: {}".format(now))
    return


# ======================================================================================================================
# Run
# ======================================================================================================================
script_dir = os.path.dirname(__file__)

if __name__ == "__main__":
    try:
        if config.state:
            state_poly = sg.retrieve_polygon(config.state)
            state_code = state_code(config.state)
        main()
    except KeyboardInterrupt:
        print "Finishing up..."
        clean_up()
        sys.exit()