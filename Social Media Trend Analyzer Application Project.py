#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import re
import streamlit as st
import boto3
from collections import Counter

# Function to separate hashtags from the sentence
def separate_hashtags(sentence):
    # Extract hashtags using regular expression
    hashtags = re.findall(r'#\w+', sentence)

    # Remove hashtags from the sentence
    clean_sentence = re.sub(r'#\w+', '', sentence).strip()

    return clean_sentence, hashtags

# Streamlit app title
st.title("Social Media Trend Analyzer Application Project")

# Input for multiple tweets
tweets = st.text_area("Enter Tweets here (one tweet per line):")

# Check if tweets are entered
if tweets:
    # Split tweets by lines and process each tweet
    tweet_lines = tweets.split('\n')
    for tweet in tweet_lines:
        # Separate hashtags from the tweet
        cleaned_sentence, extracted_hashtags = separate_hashtags(tweet)

        # Initialize AWS clients
        session = boto3.Session(
            aws_access_key_id='XXXXXXXXXXXXXXXXXX',
            aws_secret_access_key='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            region_name='us-east-1'
        )

        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table('AWS-NoSQL-Database(analyser)')

        # Store data in DynamoDB table
        table.put_item(
            Item={
                'sentence': cleaned_sentence,
                'hashtags': extracted_hashtags
            }
        )

# Retrieve data from DynamoDB
try:
    response = table.scan()
    items = response.get('Items', [])
except Exception as e:
    st.error(f"Error retrieving data from DynamoDB: {e}")
    items = []

# Prepare data for table
data_for_table = []
hashtags_list = []

for item in items:
    sentence = item.get('sentence', '')
    hashtags = item.get('hashtags', [])
    data_for_table.append((sentence, ', '.join(hashtags)))
    hashtags_list.extend(hashtags)

# Display data in table
if data_for_table:
    st.write("### List of Sentences and Hashtags from DynamoDB")
    st.table(data_for_table)

# Count occurrences of each hashtag
hashtags_counter = Counter(hashtags_list)

# Get top 5 hashtags
top_5_hashtags = dict(hashtags_counter.most_common(5))

# Display top 5 hashtags in a bar chart
st.write("### Top 5 Hashtags")
st.bar_chart(top_5_hashtags)

