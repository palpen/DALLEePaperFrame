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


TEXT_PROMPT_HASHTAG = "#dalle"
MAX_NUM_TWEETS_TO_RETRIEVE = 5


def clean_up_tweets(tweet: Tuple[int, str]) -> List[Tuple[int, str]]:
    """Returns a list of tuples containing the tweet id and the raw tweet"""
    return (
        tweet[0],
        re.sub("[#@][A-Za-z0-9_]+", "", tweet[1]).strip()
    )


def retrieve_most_recent_text_prompt(
    client: tweepy.client.Client,
    configs: Dict[str, str]
) -> Tuple[int, str]:
    """Returns a tuple containing the most recent tweet id and tweet with
    the TEXT_PROMPT_HASHTAG hashtag that will be used as the text prompt to
    generate an image using DALL-E
    """
    user_tweets = client.get_users_tweets(
        id=configs["user_id"],
        max_results=MAX_NUM_TWEETS_TO_RETRIEVE
    )
    raw_tweets = [
        (t.id, t.text) for t in user_tweets.data
        if TEXT_PROMPT_HASHTAG in t.text
    ]
    if not raw_tweets:
        return (None, "")
    return clean_up_tweets(raw_tweets[0])
