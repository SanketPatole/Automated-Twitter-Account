import re
from textblob import TextBlob
import tweepy
import pandas as pd
from replit import db
from keep_alive import keep_alive
import time
import random
from datetime import datetime
from pytz import timezone
from Quote2Image import Convert, ImgObject

tz = timezone('EST')
banned = [
  'abdl', 'addmysc', 'adulting', 'alone', 'always', 'armparty', 'asiangirl',
  'ass', 'assday', 'assworship', 'beautyblogger', 'besties', 'bikinibody',
  'boho', 'brain', 'costumes', 'curvygirls', 'date', 'dating', 'desk',
  'direct', 'dm', 'edm', 'eggplant', 'elevator', 'girlsonly', 'gloves',
  'hardworkpaysoff', 'hawks', 'hotweather', 'humpday', 'hustler', 'ice',
  'instasport', 'iphonegraphy', 'italiano', 'kansas', 'kickoff', 'killingit',
  'kissing', 'loseweight', 'lulu', 'master', 'mileycyrus', 'milf',
  'mirrorphoto', 'models', 'mustfollow', 'nasty', 'newyearsday', 'nudity',
  'overnight', 'parties', 'petite', 'pornfood', 'prettygirl', 'pushups',
  'rate', 'ravens', 'saltwater', 'samelove', 'selfharm', 'single',
  'singlelife', 'skateboarding', 'skype', 'snap', 'snapchat', 'snowstorm',
  'sopretty', 'stranger', 'streetphoto', 'sunbathing', 'swole', 'shower',
  'shit', 'tag4like', 'tagsforlikes', 'tanlines', 'todayimwearing', 'teens',
  'teen', 'thought', 'undies', 'valentinesday', 'workflow', 'Y', 'Youngmode'
]


def create_image(quote, author):
  image_name = "kk" + str(random.randint(1, 17)) + ".webp"
  img = Convert(quote=quote,
                author=author,
                fg=(21, 21, 21),
                bg=ImgObject(image=image_name, brightness=130, blur=0),
                font_size=50,
                font_type="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                width=1024,
                height=1024,
                watermark_text="Follow us @2ds_inspiration",
                watermark_font_size=40)
  img.save("quote.png")


def like_and_retweet(auth):
  api = tweepy.API(auth, wait_on_rate_limit=True)
  search_query = "#inspiration OR #quote"
  tweet_cursor = None
  try:
    tweet_cursor = tweepy.Cursor(api.search_tweets,
                                 q=search_query,
                                 tweet_mode='extended')
  except:
    print("Unable to fetch tweets to like.")
    return
  time.sleep(20)
  """
  for tweet in tweet_cursor.items(50):
    if tweet.user.screen_name == '2ds_inspiration':
      continue
    try:
      status = api.get_status(tweet.id, tweet_mode='extended')
      time.sleep(10)
      if not status.favorited:
        cleaned_tweet = ' '.join(
          re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ",
                 tweet.full_text).split())
        analysis = TextBlob(cleaned_tweet).sentiment.polarity
        if analysis <= 0.0:
          print("Did not like offensive tweet.")
          continue
        api.create_favorite(tweet.id)
        time.sleep(10)
        break
    except:
      print("Unable to like tweet.")
      break
  time.sleep(40)
  """
  for tweet in tweet_cursor.items(50):
    if tweet.user.screen_name == '2ds_inspiration':
      continue
    try:
      status = api.get_status(tweet.id, tweet_mode='extended')
      time.sleep(5)
      if not status.retweeted:
        cleaned_tweet = ' '.join(
          re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ",
                 tweet.full_text).split())
        analysis = TextBlob(cleaned_tweet).sentiment.polarity
        if analysis <= 0.0:
          print("Did not retweet offensive tweet.")
          continue
        api.retweet(tweet.id)
        time.sleep(10)
        return
    except:
      print("Unable to retweet.")
      break
  print("Could not find any tweet to retweet.")


def send_tweet(index, auth, df):
  quote = None
  author = None
  category = None
  try:
    quote = df.iloc[:, 0][index]
    author = df.iloc[:, 1][index].split(",")[0]
    category = [
      '#' + word.strip().replace('-', '')
      for word in df.iloc[:, 2][index].split(',')
      if word.strip() != 'attributed-no-source' and word.strip() not in banned
    ]
  except:
    send_tweet(index + 1, auth, df)
    return
  hashtags = '#' + str(index + 1) + ' #quote ' + ' '.join(category)
  cleaned_tweet = ' '.join(
    re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ",
           f"Author - {author}\n\n{hashtags}").split())
  analysis = TextBlob(cleaned_tweet).sentiment.polarity
  cleaned_tweet_image = ' '.join(
    re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ",
           quote).split())
  analysis_image = TextBlob(cleaned_tweet_image).sentiment.polarity
  if len(quote) > 280 or analysis < 0.01 or analysis_image < 0.01:
    send_tweet(index + 1, auth, df)
    return
  api = tweepy.API(auth, wait_on_rate_limit=True)
  create_image(quote=quote, author=author)
  try:
    status = api.update_status_with_media(
      filename="quote.png", status=f"Author - {author}\n\n{hashtags}")
  except:
    send_tweet(index + 1, auth, df)
    return
  index += 1
  with open('index.txt', 'w') as f:
    f.write(str(index))
  return


df = pd.read_parquet('quotes.parquet')
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
index = None
keep_alive()
while True:
  if datetime.now(tz) < datetime.strptime('2023-04-12',
                                          '%Y-%m-%d').astimezone():
    continue
  with open('index.txt') as f:
    index = int(f.read())
  send_tweet(index, auth, df)
  time.sleep(40)
  like_and_retweet(auth)
  time.sleep(40)
