"""
This script will be run by a cron job. It has one purpose, retrieve the last n
tweets and take the latest one with the trigger word and the text prompt
that will be used as an input in the api call to the server hosting DALL-E
"""
import re
from typing import Dict
from typing import List
from typing import Tuple

import tweepy
import yaml

TEXT_PROMPT_HASHTAG = "#dalle"
MAX_NUM_TWEETS_TO_RETRIEVE = 5


def retrieve_tweets_containing_text_prompt(
    client: tweepy.client.Client,
    configs: Dict[str, str]
) -> List[Tuple[int, str]]:
    user_tweets = client.get_users_tweets(
        id=configs["user_id"],
        max_results=MAX_NUM_TWEETS_TO_RETRIEVE
    )
    return [(t.id, t.text) for t in user_tweets.data if TEXT_PROMPT_HASHTAG in t.text]


def remove_hashtags_and_mentions_from_tweet(tweet: str) -> str:
    return re.sub("#[A-Za-z0-9_]+", "", re.sub("@[A-Za-z0-9_]+", "", tweet))


def clean_up_tweets(tweets: List[str]) -> List[Tuple[int, str]]:
    return [
        (tweet[0], remove_hashtags_and_mentions_from_tweet(tweet[1]).strip())
        for tweet in tweets
    ]


def retrieve_most_recent_text_prompt(client: tweepy.client.Client, configs: Dict[str, str]):
    raw_tweets = retrieve_tweets_containing_text_prompt(client=client, configs=configs)
    if not raw_tweets:
        raise ValueError(f"There are no text prompts containing the trigger hashtag {TEXT_PROMPT_HASHTAG}")
    text_prompts = clean_up_tweets(raw_tweets)
    return text_prompts[0]
