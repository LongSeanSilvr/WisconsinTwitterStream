"""
Python Geolocation Listener for Twitter
"""

import sys
import os
import json
import datetime
import tweepy
import textwrap
import config


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
        (user, content_readable) = pull_interesting_bits(data)
        print "{}.\nUSER: {}\nCONTENT:\n{}\n".format(str(self.num_tweets), user, content_readable)
        write_output(data, user, content_readable)
        # run until n tweets collected
        self.num_tweets += 1
        if self.num_tweets < self.tweet_limit:
            return
        else:
            print "\n{} tweets collected!\nExiting...\n".format(self.tweet_limit)
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
    return user, content_readable


def write_output(data, user, content):
    with open(os.path.join(script_dir, "output/pyglit_tweet_stream.json"), 'a') as f:
        f.write(data)
    with open(os.path.join(script_dir, "output/pyglit_tweet_stream.txt"), 'a') as f:
        f.write("user: {}\nncontent:\n{}\n\n".format(user, content))


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
    stream.filter(locations=config.bbox)


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
        main()
    except KeyboardInterrupt:
        print "Finishing up..."
        clean_up()
        sys.exit()
