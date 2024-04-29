# -*- coding: utf-8 -*-
"""Final Youtube Comment Analysis.ipynb

Automatically generated by Colaboratory.


"""

!pip install emoji
!pip install vaderSentiment
!pip install google-api-python-client











# For Fetching Comments
from googleapiclient.discovery import build
# For filtering comments
import re
# For filtering comments with just emojis
import emoji
# Analyze the sentiments of the comment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# For visualization
import matplotlib.pyplot as plt
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer











# Make sure to put in the API KEY as it won't work otherwise
API_KEY = ''# Put in your API Key

youtube = build('youtube', 'v3', developerKey=API_KEY) # initializing Youtube API

# Taking input from the user and slicing for video id
video_id = input('Enter Youtube Video URL: ')[-11:]
print("video id: " + video_id)

# Getting the channelId of the video uploader
video_response = youtube.videos().list(
    part='snippet',
    id=video_id
).execute()

# Splitting the response for channelID
video_snippet = video_response['items'][0]['snippet']
uploader_channel_id = video_snippet['channelId']
print("channel id: " + uploader_channel_id)











# Fetch comments
print("Fetching Comments...")
comments = []
nextPageToken = None
while len(comments) < 600:
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=100,  # You can fetch up to 100 comments per request
        pageToken=nextPageToken
    )
    response = request.execute()
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        # Check if the comment is not from the video uploader
        if comment['authorChannelId']['value'] != uploader_channel_id:
            comments.append(comment['textDisplay'])
    nextPageToken = response.get('nextPageToken')

    if not nextPageToken:
        break

# Print each comment with comment number and separator
print("Printing Comments...")
for i, comment in enumerate(comments, 1):
    print(f"Comment {i}: {comment}\n{'-'*50}")













hyperlink_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

threshold_ratio = 0.65

relevant_comments = []

# Inside your loop that processes comments
for comment_text in comments:

    comment_text = comment_text.lower().strip()

    emojis = emoji.emoji_count(comment_text)

    # Count text characters (excluding spaces)
    text_characters = len(re.sub(r'\s', '', comment_text))

    if (any(char.isalnum() for char in comment_text)) and not hyperlink_pattern.search(comment_text):
        if emojis == 0 or (text_characters / (text_characters + emojis)) > threshold_ratio:
            relevant_comments.append(comment_text)

# Print each relevant comment with index and separator
print("Relevant Comments:")
for i, comment in enumerate(relevant_comments, 1):
    print(f"Comment {i}: {comment}\n{'-'*50}")













f = open("ytcomments.txt", 'w', encoding='utf-8')
for idx, comment in enumerate(relevant_comments):
    f.write(str(comment)+"\n")
f.close()
print("Comments stored successfully!")














def sentiment_scores(comment, polarity):
    # Creating a SentimentIntensityAnalyzer object.
    sentiment_object = SentimentIntensityAnalyzer()

    sentiment_dict = sentiment_object.polarity_scores(comment)
    polarity.append(sentiment_dict['compound'])
    print(f"Comment: {comment.strip()}\nSentiment Scores: {sentiment_dict}\n{'-'*50}")

    return polarity

polarity = []
positive_comments = []
negative_comments = []
neutral_comments = []

with open("ytcomments.txt", 'r', encoding='utf-8') as f:
    print("Reading Comments...")
    comments = f.readlines()

print("Analysing Comments...")
for index, items in enumerate(comments):
    polarity = sentiment_scores(items, polarity)

    if polarity[-1] > 0.05:
        positive_comments.append(items)
    elif polarity[-1] < -0.05:
        negative_comments.append(items)
    else:
        neutral_comments.append(items)

print(polarity)










def classify_sentiment(polarity):
    classified_sentiments = []
    for score in polarity:
        if score > 0.05:
            classified_sentiments.append('positive')
        elif score < -0.05:
            classified_sentiments.append('negative')
        else:
            classified_sentiments.append('neutral')
    return classified_sentiments

# Example usage
classified_sentiments = classify_sentiment(polarity)

# Print comments along with comment number and classified sentiments
for i, (comment, sentiment) in enumerate(zip(comments, classified_sentiments), 1):
    print(f"Comment {i}:")
    print(f"{comment.strip()}")
    print(f"Classified Sentiment: {sentiment}\n{'-'*50}")














avg_polarity = sum(polarity) / len(polarity)
print("Average Polarity:", avg_polarity)

if avg_polarity > 0.05:
    print("The Video has got a Positive response")
elif avg_polarity < -0.05:
    print("The Video has got a Negative response")
else:
    print("The Video has got a Neutral response")

max_positive_comment = comments[polarity.index(max(polarity))]
max_negative_comment = comments[polarity.index(min(polarity))]

print("\nThe comment with most positive sentiment:")
print(max_positive_comment.strip(), "with score", max(polarity), "and length", len(max_positive_comment))

print("\nThe comment with most negative sentiment:")
print(max_negative_comment.strip(), "with score", min(polarity), "and length", len(max_negative_comment))













positive_count = len(positive_comments)
negative_count = len(negative_comments)
neutral_count = len(neutral_comments)

# labels and data for Bar chart
labels = ['Positive', 'Negative', 'Neutral']
comment_counts = [positive_count, negative_count, neutral_count]

# Creating bar chart
plt.bar(labels, comment_counts, color=['blue', 'red', 'grey'])

# Adding labels and title to the plot
plt.xlabel('Sentiment')
plt.ylabel('Comment Count')
plt.title('Sentiment Analysis of Comments')

# Displaying the chart
plt.show()













# labels and data for Bar chart
labels = ['Positive', 'Negative', 'Neutral']
comment_counts = [positive_count, negative_count, neutral_count]

plt.figure(figsize=(10, 6)) # setting size

# plotting pie chart
plt.pie(comment_counts, labels=labels)

# Displaying Pie Chart
plt.show()












import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string


# Function to preprocess a single comment
def preprocess_comment(comment):
    # Convert to lowercase
    comment = comment.lower()

    # Remove punctuation
    comment = comment.translate(str.maketrans('', '', string.punctuation))

    # Tokenize the comment
    tokens = word_tokenize(comment)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    # Join tokens back into a string
    preprocessed_comment = ' '.join(tokens)

    return preprocessed_comment

# Sentiment analysis for user provided comments
user_comments = []
num_comments = int(input("How many comments would you like to analyze? "))

# Loop to collect user comments
for i in range(num_comments):
    comment = input(f"Enter comment {i+1}: ")
    preprocessed_comment = preprocess_comment(comment)
    user_comments.append(preprocessed_comment)

print("\nAnalyzing user comments...")

# Loop to analyze each user comment
for comment in user_comments:
    print(f"\nAnalyzing comment: {comment}")
    user_polarity = sentiment_scores(comment, [])
    print("Sentiment Scores:", user_polarity)











from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

# Function to preprocess a comment
def preprocess_comment(comment):
    # Convert to lowercase
    comment = comment.lower()

    # Remove punctuation
    comment = comment.translate(str.maketrans('', '', string.punctuation))

    # Tokenize the comment
    tokens = word_tokenize(comment)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words]

    return filtered_tokens

# Function to calculate accuracy
def calculate_accuracy(predicted_sentiments, true_sentiments):
    correct_predictions = sum(1 for pred, true in zip(predicted_sentiments, true_sentiments) if pred == true)
    total_comments = len(true_sentiments)
    accuracy = correct_predictions / total_comments
    return accuracy

# Sample labeled dataset
comments = ["This movie is great!", "I hated this book.", "Neutral comment here."]
true_sentiments = ["positive", "negative", "neutral"]

# Preprocess comments
preprocessed_comments = [preprocess_comment(comment) for comment in comments]

# Predict sentiments (assuming you have a sentiment analysis model)
predicted_sentiments = ["positive", "negative", "neutral"]

# Calculate accuracy
accuracy = calculate_accuracy(predicted_sentiments, true_sentiments)
print("Accuracy:", accuracy)
