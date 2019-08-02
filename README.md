# tweet-keywords-and-entities
Extracts keywords and entities from tweets and visualizes them.

## About
This was part of my summer research project for K-State's Knowledge in Discovery and Databases Threat Intelligence project.

### top20.py
This script connects to a MongoDB database and uses Twitter's API to automatically extract tweets related to cybersecurity using simple keyword matching. It fetches only original tweets, and then stores them into the MongoDB database.

### analyze.py
This script is used to analyze the tweets that were extracted in the previous script. It does this by navigating to the proper MongoDB database and going through all the tweets, doing basic preprocessing, and generating a keyword and entity using IBM Watson's Natural Language Understanding API. It then aggregates all of the keywords/entities from the tweets, calculates the top 20 of each, and exports them to .csv files.

### script.R
This script uses the .csv file generated from the previous Python script to visualize the extracted keywords/entities. It generates a packed bubble chart, with the size of each bubble indicating the frequency of the keyword/entity and the color of the bubble indicating the sentiment (red for negative, green for positive, and yellow for neutral) that was alos exracted by the Natural Language Understanding API.
