"""
Python Twitter Location Listener
"""

import sys, os, json, datetime
import tweepy, textwrap
import config

# ======================================================================================================================
# Main Function
# ======================================================================================================================
def Main():
    WriteHeaders()
    auth = authenticate()
    start_stream(auth)
    return

# ======================================================================================================================
# Listener Class
# ======================================================================================================================
class Listener(tweepy.StreamListener):
    def __init__(self, api=None):
        self.num_tweets = 0
        self.script_dir = os.path.dirname(__file__)
        self.text_wrapper = textwrap.TextWrapper(width=70, initial_indent="    ", subsequent_indent="    ")
        self.tweet_limit = config.tweet_limit

    def on_data(self, data):

        # Use Json to decode data stream
        decoded = json.loads(data)

        # Open nodes for writing human readable ouput
        try:
            user = decoded['user']['screen_name'].encode('ascii', 'ignore')
        except KeyError:
            user = "anonymous"
        try:
            content_readable = self.text_wrapper.fill(decoded['text'].encode('ascii', 'ignore'))
        except KeyError:
            content_readable = "NULL_CONTENT"
        try:
            content = decoded['text'].encode('ascii', 'ignore')
        except KeyError:
            content = "NULL_CONTENT"

        #Write to json and human readable files
        with open(os.path.join(self.script_dir,"output/Wisconsin_tweet_stream.json"), 'a') as f:
            f.write(data)
        with open(os.path.join(self.script_dir,"output/Wisconsin_tweet_stream.txt"), 'a') as f:
            f.write("user: {}\nncontent:\n{}\n\n".format(user, content_readable))
        self.num_tweets += 1
        print "{}.\nUSER: {}\nCONTENT:\n{}\n".format(str(self.num_tweets),user, content_readable)

        #run until n tweets collected
        if self.num_tweets < self.tweet_limit:
            return True
        else:
            print "\n{} tweets collected!\nExiting...\n".format(self.tweet_limit)
            clean_up()
            sys.exit()

    def on_limit(self, track):
        print 'Limit hit! Track = {}'.format(track)
        return

    def on_error(self, status_code):
        print 'An error has occured! Status code = {}'.format(status_code)
        return True  # keep stream alive

    def on_timeout(self):
        print 'Timeout: Snoozing Zzzzzz'
        return

# ======================================================================================================================
# Program Functions
# ======================================================================================================================
def WriteHeaders():
    now = str(datetime.datetime.now())
    script_dir = os.path.dirname(__file__)
    if not os.path.isfile(os.path.join(script_dir,"output/Wisconsin_tweet_stream.json")):
        with open(os.path.join(script_dir,"output/Wisconsin_tweet_stream.json"), 'wb') as f:
            f.write("TWITTER COLLECTION\nCollection started at: {}\n\n".format(now))
    if not os.path.isfile(os.path.join(script_dir,"output/Wisconsin_tweet_stream.txt")):
        with open(os.path.join(script_dir,"output/Wisconsin_tweet_stream.txt"), 'wb') as f:
            f.write("TWITTER COLLECTION\nCollection started at: {}\n\n".format(now))
    return

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
    script_dir = os.path.dirname(__file__)
    with open(os.path.join(script_dir,"output/Wisconsin_tweet_stream.json"), 'a') as f:
        f.write("\n\nTWITTER COLLECTION ENDED: {}".format(now))
    with open(os.path.join(script_dir,"output/Wisconsin_tweet_stream.txt"), 'a') as f:
        f.write("\n\nTWITTER COLLECTION ENDED: {}".format(now))
    return


# ======================================================================================================================
# Run
# ======================================================================================================================

if __name__ == "__main__":
    try:
        Main()
    except KeyboardInterrupt:
        print "Finishing up..."
        clean_up()
        sys.exit()
