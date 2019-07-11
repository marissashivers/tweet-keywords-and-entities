from pymongo import MongoClient
import preprocessor as p
from langdetect import detect
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, KeywordsOptions, EntitiesOptions
import re
import pandas # for writing to CSV
import json

with open('credentials.json') as cred_data:
	info = json.load(cred_data)
	iam_api = info['IAM_APIKEY']

# Setup NLU API with credentials
natural_language_understanding = NaturalLanguageUnderstandingV1(
	version='2018-11-16',
	iam_apikey=iam_api,
	url='https://gateway.watsonplatform.net/natural-language-understanding/api'
)	

def clean_tweet(original_tweet):
	# Basic pre-processing
	# Removing URLS, @, #, reserved, emojis, :)
	p.set_options(p.OPT.URL, p.OPT.MENTION, p.OPT.RESERVED, p.OPT.EMOJI, p.OPT.SMILEY)
	cleaned_tweet = p.clean(original_tweet)

	# Remove emojis (doesn't work for all of them...)
	RE_EMOJI = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)
	cleaned_tweet = RE_EMOJI.sub(r'', cleaned_tweet)

	# Remove escape characters
	cleaned_tweet = re.sub('&lt;/?[a-z]+&gt;', '', cleaned_tweet)
	cleaned_tweet = cleaned_tweet.replace('&amp;amp;', '&')
	cleaned_tweet = cleaned_tweet.replace('&amp;', '&')
	cleaned_tweet = cleaned_tweet.replace('$&gt;', '')
	cleaned_tweet = cleaned_tweet.replace('&gt;', '')
	cleaned_tweet = cleaned_tweet.replace('#', '')

	return cleaned_tweet

def main():
	# connecting to MongoDB
	myclient = MongoClient()
	myclient = MongoClient("mongodb://localhost:27017/")

	# Navigate to proper database and collection
	mydb_input = input('Enter the name of your MongoDB database: ')
	mydb = myclient[mydb_input]
	mycol_input = input('Enter the name of your MongoDB collection: ')
	mycol = mydb[mycol_input]

	# Initialize list of dictionaries
	keywords_list = []
	entities_list = []

	for document in mycol.find():
		try:	
			if ((detect(str(document['tweet'])) == 'en')): # if the tweet is english
				# clean the tweet
				cleaned_tweet = clean_tweet(str(document['tweet']))
				# generate response from NLU
				response = natural_language_understanding.analyze(
					text=cleaned_tweet,
					features=Features(
							entities=EntitiesOptions(sentiment=True, limit=1),
							keywords=KeywordsOptions(sentiment=True, limit=1))).get_result()
				# KEYWORDS: generate/update dict entry for keyword
				try:
					keyword_found = False;
					for item in keywords_list:
						if item['text'] == response['keywords'][0]['text']:
							item['count'] += 1
							keyword_found = True;
							break;
					if not keyword_found:
						# create keyword_dict entry of output from NLU
						keyword_entry = {
							'text': response['keywords'][0]['text'],
							'count': response['keywords'][0]['count'],
							'sentiment': response['keywords'][0]['sentiment']['score']
						}
						keywords_list.append(keyword_entry)
				except Exception as e:
					print('Error adding keyword: ' + str(e))

				# ENTITIES: generate/update dict entry for keyword
				try:
					entity_found = False;
					for item in entities_list:
						if item['text'] == response['entities'][0]['text']:
							item['count'] += 1
							entity_found = True;
							break;
					if not entity_found:
						# create entity_dict entry
						entity_entry = {
							'text': response['entities'][0]['text'],
							'count': response['entities'][0]['count'],
							'sentiment': response['entities'][0]['sentiment']['score']
						}
						entities_list.append(entity_entry)
				except Exception as e:
					print('Error adding entity: ' + str(e))
		except Exception as e:
			print('Error processing tweet: ' + str(e))

	# top 20 only
	keywords_sorted = sorted(keywords_list, key = lambda i: i['count'], reverse=True)
	entities_sorted = sorted(entities_list, key = lambda i: i['count'], reverse=True)

	if len(keywords_sorted) > 20:
		keywords_sorted[:20]
	if len(entities_sorted) > 20:
		entities_sorted[:20]


	# Creating a dataframe using pandas
	df_keywords = pandas.DataFrame(keywords_sorted)
	df_keywords_columns = ['text', 'count', 'sentiment']
	df_keywords = df_keywords.reindex(columns=df_keywords_columns)

	df_entities = pandas.DataFrame(entities_sorted)
	df_entities_columns = ['text', 'count', 'sentiment']
	df_entities = df_entities.reindex(columns=df_entities_columns)

	# Writing the data to a .csv file
	filename_keywords = input('Enter a .csv file name to save the keywords data to: ')
	df_keywords.to_csv(filename_keywords, encoding='utf-8', index=False)
	print('File successfully saved!')
	print()
	filename_entities = input('Enter a .csv file name to save the entities data to: ')
	df_entities.to_csv(filename_entities, encoding='utf-8', index=False)
	print('File successfully saved!')

if __name__ == '__main__':
	main()
