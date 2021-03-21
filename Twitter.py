# Import modules
import requests
import json
import os
import re
from textblob import TextBlob
import pandas as pd
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import time

def Get_Twitter_Input(person,company):
    start = time.time()
    print("Start: Creating username\n")
    # Removing whitespaces in name
    person = person.split(' ')
    company = company.split(' ')
    person_twitter = ''
    company_twitter = ''
    for item in person:
        person_twitter = person_twitter+item
    for item in company:
        company_twitter = company_twitter+item
    # Convert all input data to lowercase for twitter to handle
    person_twitter = person_twitter.lower()
    company_twitter = company_twitter.lower()
    # Call function to get tweets
    Get_Twitter(person_twitter,company_twitter,bearer_token)
    end = time.time()
    # Display time needed to parse user input
    print("Runtime for creating username: ",(end-start))
    print("End: Creating username\n")

# Get tweets from person and company account
def Get_Twitter(person,company,bearer_token):
    print("Start: Getting tweets\n")
    start = time.time()
    # Date is used to get all tweets since account opening for sentiment analysis
    person_created_date = ''
    company_created_date = ''
    person_twitter_username = ''
    # Bearer token needs to be refreshed regularly (10 days)
    headers = {
        'Authorization' : bearer_token
    }

    # Find all twitter details for a person (name, username, date of creation etc)
    personURL = "https://api.twitter.com/2/users/by"
    person_params={
        "usernames": person,
        "user.fields": "created_at,description,location,verified,profile_image_url",
        "expansions": "pinned_tweet_id",
        "tweet.fields": "author_id,text",
    }
    response = requests.request("GET", url=personURL,params=person_params, headers=headers)
    response = response.json()
    if 'errors' in response:
        # Account has been suspended/not on twitter
        f.write(person+' not found on Twitter\n') 
    else:
        # Write all available data to file 
        for item in response['data']:
            if item['name']:
                f.write('Name: '+item['name'])
                f.write('\n')
            if item['username']:
                f.write('Twitter username: '+item['username'])
                person_twitter_username = item['username']
                f.write('\n')
            if item['id']:
                f.write('Twitter user id: '+item['id'])
                f.write('\n')
            if item['profile_image_url']:
                f.write('Profile picture link: '+item['profile_image_url'])
                f.write('\n')
            if item['verified']:
                f.write('Account verification: '+str(item['verified']))
                f.write('\n')
            if item['created_at']:
                f.write('Created date: '+item['created_at'])
                person_created_date = item['created_at']
                f.write('\n')
            if item['location']:
                f.write('Location: '+item['location'])
                f.write('\n')
            if item['description']:
                f.write('Description: '+item['description'])
                f.write('\n')
        f.write('\n')

    # Find all details for a company
    companyURL = "https://api.twitter.com/2/users/by"
    company_params={
        "usernames": company,
        "user.fields": "created_at,description,location,verified,profile_image_url",
        "expansions": "pinned_tweet_id",
        "tweet.fields": "author_id,text",
    }
    response = requests.request("GET", url=companyURL,params=company_params, headers=headers)
    response = response.json()
    # Write all available data to file
    for item in response['data']:
        if item['name']:
            f.write('Company Name: '+item['name'])
            f.write('\n')
        if item['username']:
            f.write('Twitter username: '+item['username'])
            f.write('\n')
        if item['id']:
            f.write('Twitter user id: '+item['id'])
            f.write('\n')
        if item['profile_image_url']:
            f.write('Logo link: '+item['profile_image_url'])
            f.write('\n')
        if item['verified']:
            f.write('Account verification: '+str(item['verified']))
            f.write('\n')
        if item['created_at']:
            f.write('Created date: '+item['created_at'])
            company_created_date = item['created_at']
            f.write('\n')
        if 'location' in item:
            f.write('Location: '+item['location'])
            f.write('\n')
        if item['description']:
            f.write('Description: '+item['description'])
            f.write('\n')
        f.write('\n')

    baseURL = 'https://api.twitter.com/1.1/search/tweets.json'
    # Find all tweets other users have tweeted about company
    trending = '#'+company
    params={
        'q':trending,
        'count':'100',
        'lang':'en',
        'since_id':company_created_date
    }
    response1 = requests.get(baseURL,params=params, headers=headers)
    response1 = response1.json()
    text = []
    for item in response1['statuses']:
        text.append(item['text'])
    # Create a datframe for all tweets
    df = pd.DataFrame(text,columns=["Tweets"])

    print("Start: Getting sentiment analysis\n")
    start_analysis = time.time()
    # Clean up tweets in dataframe
    df['Tweets'] = df['Tweets'].apply(cleanText)
    # Create a new datframe with all evalauted tweets (pos/neg/neu)
    print(df)
    new_df = getSentiment(df)
    if new_df == 0:
        f.write("Average sentiment not found for company. Data insufficient for analysis")
        f.write('\n')
    else:
        # sentiment is sum of all scores obtained during sentiment analysis
        sentiment = sum(new_df['compound'])
        # Write average sentiment into file
        f.write("Average sentiment of company's tweets is: "+getAverageSentiment(sentiment))
        f.write('\n')
        # Count no.of positive, neutral and negative tweets
        counts = df['Sentiment'].value_counts()
        print(counts)
        print(new_df)
    end_analysis =  time.time()
    # Display runtime for sentiment analysis
    print("Runtime for getting sentiment analysis: ",(end_analysis-start_analysis))
    print("\nEnd: Getting sentiment analysis\n")

    # Find all tweets person has tweeted since account creation
    twitter_person = '@'+person_twitter_username
    params={
        'q':twitter_person,
        'count':'100',
        'lang':'en',
        'since_id':person_created_date
    }
    #
    response2 = requests.get(baseURL,params=params, headers=headers)
    response2 = response2.json()
    if response2['statuses'] == []:
        f.write('Person is not a regular twitter user. ')
        f.write('No recent tweets to display for '+person)
        f.write('\n')
    # Display time taken to run getting tweets
    end = time.time()
    print("Runtime for getting tweets: ",(end-start))
    print("\nEnd: Getting tweets\n")

# Clean up all tweets
def cleanText(text):
  text = re.sub('@[A-za-z0-9]+','', text) # removing mentions
  text = re.sub('#', "", text) # removing hashtags
  text = re.sub('RT[\s]+', "", text) # removing re-tweets (RT) 
  text = re.sub("https?:\/\/\S+", "", text) # removing hyperlink
  text = re.sub("\n","",text) # removing nextline characters
  return text

# Get sentiment for all tweets using nltk Vader sentiment analyzer
def getSentiment(tw_list):
    if tw_list.empty:
        # Check if datframe is empty
        print('\nNo tweets to analyze!\n')
        return 0
    for index, row in tw_list['Tweets'].iteritems():
      # Score all tweets in dataframe
        score = SentimentIntensityAnalyzer().polarity_scores(row)
        neg = score['neg']
        neu = score['neu']
        pos = score['pos']
        comp = score['compound']
        # Create column 'Sentiment' and based on score, label tweets
        if neg > pos:
            tw_list.loc[index, 'Sentiment'] = 'negative'
        elif pos > neg:
            tw_list.loc[index, 'Sentiment'] = 'positive'
        else:
            tw_list.loc[index, 'Sentiment'] = 'neutral'
        # Append all results to dataframe
        tw_list.loc[index, 'Negative'] = neg
        tw_list.loc[index, 'Neutral'] = neu
        tw_list.loc[index, 'Positive'] = pos
        tw_list.loc[index, 'compound'] = comp
        # Display full text and label for text
        print(tw_list.loc[index,['Tweets','Sentiment']])
    # Return evaluated dataframe
    print(tw_list)
    return tw_list

# Output for average sentiment
def getAverageSentiment(score):
  if score < 0:
    return "Negative"
  elif score == 0:
    return "Neutral"
  else:
    return "Positive"

# Driver code
# Ask user for query to search for
company = input("Enter company name: ")
twitter_name = input("Enter twitter username/person name: ")

# Write data to this file
f = open('data1.txt','w')

# Read username and password from config.txt
file = open('config.txt')
lines = file.readlines()
# Authenticate twitter access to API
bearer_token = lines[2]
# Get twitter data for person and company
Get_Twitter_Input(twitter_name,company)
