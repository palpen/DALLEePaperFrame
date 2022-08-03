import tweepy
import tweets_utils
import yaml


with open("../config.yml", "r") as stream:
	try:
		configs = yaml.safe_load(stream)
	except yaml.YAMLError as exc:
		print(exc)

twitter_api_keys = configs["twitter_api_keys"]
client = tweepy.Client(
	bearer_token=twitter_api_keys["bearer_token"],
	consumer_key=twitter_api_keys["consumer_key"],
	consumer_secret=twitter_api_keys["consumer_secret"],
	access_token=twitter_api_keys["access_token_key"],
	access_token_secret=twitter_api_keys["access_token_secret"]
)

most_recent_text_prompt = tweets_utils.retrieve_most_recent_text_prompt(client=client, configs=configs)

print(most_recent_text_prompt)

# upload to twitter
# Get id of most latest tweet
# Reply to most latest tweet with attached image

client.create_tweet(text='Some reply', in_reply_to_tweet_id=1554678399125360640)
