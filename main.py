import os
import time
import tweepy
import logging
import requests
from datetime import datetime

bot_token       = os.environ['TELEGRAM_TOKEN']
URL             = f"https://api.telegram.org/bot{bot_token}/"
chat_id         = os.environ['TELEGRAM_CHAT_ID']
consumer_key    = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token    = os.environ['ACCESS_TOKEN']
access_secret   = os.environ['ACCESS_SECRET']
username        = os.environ['TWITTER_USERNAME'] #page link
get_update      = os.environ['GET_UPDATE'] #update time

logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)
last_text = []

def send_message(text):
    last_text.append(text)
    data={'chat_id': chat_id, 'text': text}
    request = requests.post(f"{URL}sendMessage",data=data)
    return request.json()

def get_all_tweets(tweet):
    screen_name = username
    last_tweet_id = tweet.id
    last_tweets = []
    new_tweets = api.user_timeline(screen_name = screen_name, count=10)
    last_tweets.extend(new_tweets)
    oldest = last_tweets[-1].id - 1
    while len(new_tweets) > 0 and oldest >= last_tweet_id:
        new_tweets = api.user_timeline(screen_name = screen_name,count=10, max_id=oldest)
        last_tweets.extend(new_tweets)
        oldest =last_tweets[-1].id - 1
    outtweets = [tweet.id for tweet in last_tweets]
    return outtweets

def get_all_tweets_in_thread_after_this(twit_id):
    thread = []
    hasReply = True
    res = api.get_status(twit_id, tweet_mode='extended')
    all_till_thread = get_all_tweets(res)
    thread.append(res)
    if all_till_thread[-1] > res.id:
        return thread
    startIndex = all_till_thread.index(res.id)
    quietLong = 0
    while startIndex!=0 and quietLong<25:
        now_index = startIndex-1
        now_tweet = api.get_status(all_till_thread[now_index], tweet_mode='extended')
        if now_tweet.in_reply_to_status_id == thread[-1].id:
            quietLong = 0
            thread.append(now_tweet)
        else:
            quietLong = quietLong + 1
        startIndex = now_index
    return thread

def get_all_tweets_in_thread_before_this(twit_id):
    thread = []
    hasReply = True
    res = api.get_status(twit_id, tweet_mode='extended')
    while res.in_reply_to_status_id is not None:
        res = api.get_status(res.in_reply_to_status_id, tweet_mode='extended')
        thread.append(res)
    return thread[::-1]

def get_all_tweets_in_thread(twit_id):
    tweetsAll = []
    tweetsAll = get_all_tweets_in_thread_before_this(twit_id)
    tweetsAll.extend(get_all_tweets_in_thread_after_this(twit_id))
    return tweetsAll

def print_all_tweet(tweets):
    list=[]
    last_date     = datetime.now().date()
    lastday_tweet = datetime.date(tweets[0].created_at)
    if len(tweets)>0:
        for twit_id in range(len(tweets)):
            list.append(tweets[twit_id].full_text)
    last_tweet = ' '.join(list)
    if (last_date == lastday_tweet):
        if last_tweet not in last_text:
            send_message(text=last_tweet)

def tweet_update():
    t_id = []
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    tweets = api.user_timeline(screen_name = username,tweet_mode='extended', count=10)
    last_date     = datetime.now().date()
    lastday_tweet = datetime.date(tweets[0].created_at)
    for tweet in tweets:
        created_at = tweet.created_at
        t_id.append(tweet.id)
    last_tweets = get_all_tweets_in_thread(t_id[0])
    print_all_tweet(last_tweets)

while True:
    tweet_update()
    time.sleep(int(get_update))
