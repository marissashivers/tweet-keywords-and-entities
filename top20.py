from pymongo import MongoClient
import tweepy
import json

# connecting to MongoDB
myclient = MongoClient()
myclient = MongoClient("mongodb://localhost:27017/")

# load Twitter API credentials
with open('credentials.json') as cred_data:
	info = json.load(cred_data)
	consumer_key = info['CONSUMER_KEY']
	consumer_secret = info['CONSUMER_SECRET']
	access_key = info['ACCESS_KEY']
	access_secret = info['ACCESS_SECRET']

# Navigate to proper database and collection
mydb_input = input('Enter the name of your MongoDB database: ')
mydb = myclient[mydb_input]
mycol_input = input('Enter the name of your MongoDB collection: ')
mycol = mydb[mycol_input]

# DROP THE CURRENT COLLECTION/WIPE FRESH
# *** DELETE THIS IF STREAMING TWEETS!!! ***
mycol.drop()
mycol = mydb['top20new']

# Creating the authentication object
auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)

# Creating the api object while passing in auth information
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

###############################################

search_query = ['"0day" OR "zero day" OR "vulnerability" OR "exploit" OR "cyber" OR "cybersecurity" OR "ddos" OR "sql injection" OR "remote code execution"']
maxTweets = 20
tweetsPerQry = 10

# If results from a specific ID onwards are required, set since_id to that ID.
# else default to no lower limit, go as far back as API allows
sinceId = None

# If results only below a specific ID are, set max_id to that ID.
# else default to no upper limit, start from the most recent tweet matching the search query.
max_id = -1

tweetCount = 0
print('Downloading max {0} tweets'.format(maxTweets))

# downloading tweets...
# We are using tweet_mode='extended' to get FULL tweet
while tweetCount < maxTweets:
	try:
		if (max_id <= 0):
			if (not sinceId):
				new_tweets = api.search(q=search_query, count=tweetsPerQry, tweet_mode='extended') #tweet_mode = 'extended'
			else:
				new_tweets = api.search(q=search_query, count=tweetsPerQry, since_id=sinceId, tweet_mode='extended')
		else:
			if (not sinceId):
				new_tweets = api.search(q=search_query, count=tweetsPerQry, max_id=str(max_id - 1), tweet_mode='extended')
			else:
				new_tweets = api.search(q=search_query, count=tweetsPerQry,
	                                            max_id=str(max_id - 1),
	                                            since_id=sinceId,
	                                            tweet_mode='extended')
		if not new_tweets:
			print('No more tweets found')
			break

		for status in new_tweets:
			# if the status is NOT a retweet
			if status.full_text[0:3] != 'RT ' and not hasattr(status, 'retweeted_status'):
				try: #for tweets >140 characters
					dict = {'username': status.user.screen_name, 
					'tweet': status._json['extended_tweet'],
					'timestamp': str(status.created_at),
					'retweet': 'false'
					}
					mycol.insert_one(dict)
					tweetCount += 1
				except:
					try: #for tweets <= 140 characters
						dict = {'username': status.user.screen_name, 
						'tweet': status._json['full_text'],
						'timestamp': str(status.created_at),
						}
						mycol.insert_one(dict)
						tweetCount += 1
					except Exception as e:
						print(e)
		# end for loop
		#tweetCount += len(new_tweets)
		print('Downloaded{0} tweets'.format(tweetCount))
		max_id=new_tweets[-1].id

	except tweepy.TweepError as e:
		print('some error: ' + str(e))
		break

print('Downloaded {0} tweets'.format(tweetCount))
