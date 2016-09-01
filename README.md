# PyGLiT  (Python Geolocation Listener for Twitter)  
Listens in on and records a live stream of tweets originating from within a specified state or custom bounding box

## Usage:  
```python pyglit.py```

## Dependencies
In order to use pyglit you will have to install the following dependencies:  
* tweepy: `pip install tweepy`  
* shapely: `pip install shapely`

## Setting up config.py
Before running pyglit, you will need to set your preferences in config.py. There are three main parameters you need to set:  

##### Credentials:
* Before you anything else, you will need to [register an app with Twitter](https://apps.twitter.com/app/new). Doing so will
take you to a page listing your newly created consumer key/token and consumer secret. Copy and paste these into the appropriate
fields of config.py.  
* Next you will need to [create an access key/token and access secret](https://dev.twitter.com/oauth/overview/application-owner-access-tokens).
After doing so, paste these in to the appropriate fields in Config.py.  

##### Target Location:
For location you have two options:  
* Specify the name of a state (e.g. `state = new york`)
  * if a state name is specified, pyglit ignores whatever is in the `bbox` variable
  * state names may be upper or lower case
* Supply the coordinates for a custom bounding box (e.g. `bbox = [-92.19,42.54,-86.70,47.08]`)  
  * __NB:__ if you choose this option, set `state = None` so that pyglit ignores the `state` variable.

##### Tweet max:
* set the max number of tweets you would like to collect. Upon hitting the limit, pyglit will clean up and exit.





