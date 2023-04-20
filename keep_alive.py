from flask import Flask
from threading import Thread
import tweepy
from textblob import TextBlob
import time
import random
from datetime import datetime
from pytz import timezone
import re
from replit import db

tz = timezone('EST')
app = Flask('')


@app.route('/')
def home():
  return "I'm alive!"


def run_unfollow_people_smart():

  twitter_auth_keys = {
    "consumer_key": db['consumer_key'],
    "consumer_secret": db['consumer_secret'],
    "access_token": db['access_token'],
    "access_token_secret": db['access_token_secret']
  }
  auth = tweepy.OAuthHandler(twitter_auth_keys['consumer_key'],
                             twitter_auth_keys['consumer_secret'])
  auth.set_access_token(twitter_auth_keys['access_token'],
                        twitter_auth_keys['access_token_secret'])

  def unfollow_people_smart(auth):
    api = tweepy.API(auth, wait_on_rate_limit=True)
    unfollowers = []
    user_screen_names = []
    try:
      with open(f'{str((datetime.now(tz).weekday())+1)%6}.txt') as f:
        user_screen_names = f.read().split('\n')
    except:
      print('Followers file is not present')
      return
    try:
      for relationship in api.lookup_friendships(
          screen_name=user_screen_names):
        if not relationship.is_followed_by:
          unfollowers.append(relationship.screen_name)
    except:
      print('Unable to fetch unfollowers list.')
      return
    time.sleep(60)
    for screen_name in unfollowers:
      try:
        api.destroy_friendship(screen_name=screen_name)
      except Exception as e:
        print(e)
      time.sleep(10 * 60)

  while True:
    if datetime.now(tz).hour == 0 and datetime.now(
        tz).minute > 10 and datetime.now(tz).minute < 20 and datetime.now(
          tz).weekday() in [0, 1, 2, 3, 4, 5, 6]:
      print("It's smartly unfollowing unfollowers time")
      unfollow_people_smart(auth)
    time.sleep(5 * 60)


def run_follow_relevant_people():
  twitter_auth_keys = {
    "consumer_key": db['consumer_key'],
    "consumer_secret": db['consumer_secret'],
    "access_token": db['access_token'],
    "access_token_secret": db['access_token_secret']
  }
  auth = tweepy.OAuthHandler(twitter_auth_keys['consumer_key'],
                             twitter_auth_keys['consumer_secret'])
  auth.set_access_token(twitter_auth_keys['access_token'],
                        twitter_auth_keys['access_token_secret'])

  def follow_relevant_people(auth):
    api = tweepy.API(auth, wait_on_rate_limit=True)
    search_query = "#inspiration OR #quote"
    to_follow_screen_names = []
    to_follow_users_list = []
    for page in tweepy.Cursor(api.search_tweets, q=search_query,
                              count=100).pages(10):
      user_ids = []
      for tweet in page:
        userid = tweet.user.id
        if userid not in user_ids:
          user_ids.append(tweet.user.id)
      time.sleep(50)
      user_screen_names = []
      for relationship in api.lookup_friendships(user_id=user_ids):
        if not relationship.is_following and relationship.screen_name not in to_follow_screen_names:
          to_follow_screen_names.append(relationship.screen_name)
          user_screen_names.append(relationship.screen_name)
      time.sleep(50)
      users = api.lookup_users(screen_name=user_screen_names)
      time.sleep(50)
      for user in users:
        to_follow_users_list.append(user)
    try:
      for user in random.sample(to_follow_users_list, 100):
        user.follow()
        time.sleep(60 * 10)
    except:
      print("Follow lmit exceeded.")
    time.sleep(60 * 10)
    followers = []
    for page in tweepy.Cursor(api.get_followers, count=200).pages(5):
      for user in page:
        if not user.following:
          followers.append(user)
        time.sleep(120)
    sample_users = random.sample(followers, 50)
    try:
      for user in sample_users:
        user.follow()
        time.sleep(10 * 60)
    except:
      print("Follow lmit exceeded.")
    log_screen_names = [
      u.screen_name for u in to_follow_screen_names.append(sample_users)
    ]
    with open(f'{str(datetime.now(tz).weekday())}.txt', 'w') as f:
      f.write('\n'.join(log_screen_names))

  while True:
    if datetime.now(tz).hour == 0 and datetime.now(
        tz).minute > 0 and datetime.now(tz).minute < 10 and datetime.now(
          tz).weekday() in [0, 1, 2, 3, 4, 5, 6]:
      print("It's following relevant people time")
      follow_relevant_people(auth)
    time.sleep(5 * 60)


def keep_alive_n_delete_tweets():

  def delete_tweet(auth, tweet):
    api = tweepy.API(auth, wait_on_rate_limit=True)
    cleaned_tweet = ' '.join(
      re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ",
             tweet.text).split())
    blob = TextBlob(cleaned_tweet)
    polarity_score = blob.sentiment.polarity
    if polarity_score <= 0.01:
      api.destroy_status(tweet.id)
      print(f"deleted tweet {tweet.id}")

  startDate = datetime(2023, 4, 1, 0, 0, 0, tzinfo=timezone('UTC'))
  endDate = datetime(2023, 4, 7, 0, 0, 0, tzinfo=timezone('UTC'))

  twitter_auth_keys = {
    "consumer_key": db['consumer_key'],
    "consumer_secret": db['consumer_secret'],
    "access_token": db['access_token'],
    "access_token_secret": db['access_token_secret']
  }
  auth = tweepy.OAuthHandler(twitter_auth_keys['consumer_key'],
                             twitter_auth_keys['consumer_secret'])
  auth.set_access_token(twitter_auth_keys['access_token'],
                        twitter_auth_keys['access_token_secret'])
  api = tweepy.API(auth, wait_on_rate_limit=True)

  tmpTweets = api.user_timeline()
  for tweet in tmpTweets:
    if tweet.created_at.replace(
        tzinfo=timezone('UTC')) < endDate and tweet.created_at.replace(
          tzinfo=timezone('UTC')) > startDate:
      delete_tweet(auth, tweet)
      time.sleep(600)
  while (tmpTweets[-1].created_at.replace(tzinfo=timezone('UTC')) > startDate):
    tmpTweets = api.user_timeline(max_id=tmpTweets[-1].id)
    for tweet in tmpTweets:
      if tweet.created_at.replace(
          tzinfo=timezone('UTC')) < endDate and tweet.created_at.replace(
            tzinfo=timezone('UTC')) > startDate:
        delete_tweet(auth, tweet)
        time.sleep(600)
    time.sleep(600)


def run():
  app.run(host='0.0.0.0', port=8080)


def keep_alive():
  t1 = Thread(target=run)
  t1.start()
  #t2 = Thread(target=run_follow_relevant_people)
  #t2.start()
  #t3 = Thread(target=run_unfollow_people_smart)
  #t3.start()
  #t2 = Thread(target=keep_alive_n_delete_tweets)
  #t2.start()
