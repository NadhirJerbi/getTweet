from textblob import TextBlob 
import tweepy
import time
import re

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

client = tweepy.Client(bearer_token="your tweet project bearer_token ")

def clean_tweet(tweet,search):
    twt = tweet.lower()
    twt = re.sub("'", "", twt) # to avoid removing contractions in english
    twt = re.sub("@[A-Za-z0-9_]+","", twt) #remove  users
    twt = re.sub("#[A-Za-z0-9_]+","", twt) #remove  hashtags
    twt = re.sub(r'http\S+', '', twt) #remove  links
    twt = re.sub(r'www.\S+', '', twt) #remove  links
    twt = re.sub('[()!?]', ' ', twt) #remove punctuations
    twt = re.sub('\[.*?\]',' ', twt) #remove punctuations
    twt = re.sub("[^a-z0-9]"," ", twt) #filtering non-alphanumeric characters
    twt = re.sub(search.lower()," ", twt) #remove query search
    twt = twt.split()
    twt = ' '.join([w for w in twt if len(w)>3]) # remove all words < 3
    return twt
def get_sentiment(text):
  analysis = TextBlob(text)
  if analysis.sentiment[0]>0:
      return'Positive'  
  elif analysis.sentiment[0]<0:
      return'Negative'
  else:
      return'Neutral'

#connect to firbase
cred = credentials.Certificate("./test-fb63e-firebase-adminsdk-a79mv-84419f4307.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://test-fb63e-default-rtdb.firebaseio.com/'
})

search="tesla"
while True:
    #get tweet 
    tweets = client.search_recent_tweets(query=search, tweet_fields=['created_at'], max_results=100)
    #collection database ref
    ref = db.reference('/tweet')
    #tweet clean 
    for tweet in tweets.data:
        #delete users
        text = clean_tweet(tweet.text,search)
        #push data to database
        ref.update({
                tweet.id: {
                    'tweet_text': text,
                    'Date':str(tweet.created_at),
                    'sentiment':get_sentiment(text)
                }  
        })
    print('data stored')
    time.sleep(10)
