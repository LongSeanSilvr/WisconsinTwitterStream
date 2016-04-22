# PyGLiT  (Python Geolocation Listener for Twitter)  
Listens in on and records a live stream of tweets originating from within a specified state or custom bounding box

### Usage:  
```python pyglit.py```

### Dependencies
In order to use pyglit you will have to install the following dependencies:  
* tweepy: 'pip install tweepy`  
* shapely `pip install shapely`

### Setting up config.py
Before running pyglit, you will need to set your preferences in config.py. There are three main parameters you need to set:  
  
  #### Credentials:
  * Before you anything else, you will need to [register an app with Twitter](https://apps.twitter.com/app/new). Doing so will
  take you to a page listing your newly created consumer key/token and consumer secret. Copy and paste these into the appropriate
  fields of config.py.
  * Next you will need to [create an access key/token and access secret](https://dev.twitter.com/oauth/overview/application-owner-access-tokens).
  After doing so, paste these in to the appropriate fields in Config.py.
  
  #### Target Location:





