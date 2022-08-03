"""
This script will be run by a cron job. It has one purpose, retrieve the last n
tweets and take the latest one with the trigger word and the text prompt
that will be used as an input in the api call to the server hosting DALL-E
"""
import re
from typing import Dict
from typing import List

import tweepy
import yaml


def retrieve_tweets_containing_text_prompt(
	client: tweepy.client.Client,
	configs: Dict[str, str]
) -> List[str]:
	user_tweets = client.get_users_tweets(id=configs["user_id"], max_results=20)
	return [t.text for t in user_tweets.data if '#genimg' in t.text]


def remove_hashtags_and_mentions_from_tweet(tweet: str) -> str:
	return re.sub("#[A-Za-z0-9_]+", "", re.sub("@[A-Za-z0-9_]+", "", tweet))


def clean_up_tweets(tweets: List[str]) -> List[str]:
	return [remove_hashtags_and_mentions_from_tweet(tweet).strip() for tweet in tweets]


def retrieve_most_recent_text_prompt(client: tweepy.client.Client, configs: Dict[str, str]):
	raw_tweets = retrieve_tweets_containing_text_prompt(client=client, configs=configs)
	if not raw_tweets:
		raise ValueError("There are no text prompts containing the trigger hashtag #genimg")
	text_prompts = clean_up_tweets(raw_tweets)
	return text_prompts[0]
