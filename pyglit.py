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


# ======================================================================================================================
# Main Function
# ======================================================================================================================
def main():
    write_headers()
    auth = authenticate()
    start_stream(auth)
    return


# ======================================================================================================================
# Listener Class
# ======================================================================================================================
class Listener(tweepy.StreamListener):
    def __init__(self, api=None):
        self.num_tweets = 0
        self.tweet_limit = config.tweet_limit

    def on_data(self, data):
        if config.state:
            if state_filter(data):
                (user, content_readable, location) = pull_interesting_bits(data)
                print "{}.\nUSER: {}\nLOCATION: {}\nCONTENT:\n{}\n".format(str(self.num_tweets), user, location,
                                                                           content_readable)
                write_output(data, user, location, content_readable)
                self.num_tweets += 1
            else:
                pass
        else:
            (user, content_readable, location) = pull_interesting_bits(data)
            print "{}.\nUSER: {}\nLOCATION: {}\nCONTENT:\n{}\n".format(str(self.num_tweets), user, location,
                                                                       content_readable)
            write_output(data, user, location, content_readable)
            self.num_tweets += 1

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
script_dir = os.path.dirname(__file__)


def write_headers():
    now = str(datetime.datetime.now())

    # make output/directory if one does not exist
    if not os.path.exists(os.path.join(script_dir, "output/")):
        os.makedirs(os.path.join(script_dir, "output/"))

    # write json to json file
    if not os.path.isfile(os.path.join(script_dir, "output/pyglit_tweet_stream.json")):
        with open(os.path.join(script_dir, "output/pyglit_tweet_stream.json"), 'wb') as f:
            f.write("COLLECTION STARTED AT: {}\n\n".format(now))
    # write txt to a human-readable file for spot-checking
    if not os.path.isfile(os.path.join(script_dir, "output/pyglit_tweet_stream.txt")):
        with open(os.path.join(script_dir, "output/pyglit_tweet_stream.txt"), 'wb') as f:
            f.write("COLLECTION STARTED AT: {}\n\n".format(now))
    return


def pull_interesting_bits(data):
    decoded = json.loads(data)
    text_wrapper = textwrap.TextWrapper(width=70, initial_indent="    ", subsequent_indent="    ")
    try:
        user = decoded['user']['screen_name'].encode('ascii', 'ignore')
    except KeyError:
        user = "anonymous"
    try:
        content_readable = text_wrapper.fill(decoded['text'].encode('ascii', 'ignore'))
    except KeyError:
        content_readable = "NULL_CONTENT"
    try:
        location = decoded['place']['full_name'].encode('ascii', 'ignore')
    except KeyError:
        location = "NULL_CONTENT"
    return user, content_readable, location


def write_output(data, user, location, content):
    with open(os.path.join(script_dir, "output/pyglit_tweet_stream.json"), 'a') as f:
        f.write(data)
    with open(os.path.join(script_dir, "output/pyglit_tweet_stream.txt"), 'a') as f:
        f.write("user: {}\nlocation: {}\ncontent:\n{}\n\n".format(user, location, content))


def authenticate():
    c_tok = config.consumer_token
    c_sec = config.consumer_secret
    acc_tok = config.access_token
    acc_sec = config.access_secret

    auth = tweepy.OAuthHandler(c_tok, c_sec)
    auth.set_access_token(acc_tok, acc_sec)

    return auth


def start_stream(auth):
    stream = tweepy.Stream(auth, listener=Listener())
    if config.state:
        bbox = sg.retrieve_bbox(config.state)
    elif config.bbox:
        bbox = config.bbox
    else:
        sys.exit("ERROR: You must specify either the state of interest or a bounding box in config.py!")
    stream.filter(locations=bbox)


def state_filter(json_obj):
    # ToDo: Clean up ifelse logic here
    tweet = json.loads(json_obj)
    try:
        if config.state:
            try:
                if tweet['place']['full_name'] is not None:
                    name = tweet['place']['full_name']
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
