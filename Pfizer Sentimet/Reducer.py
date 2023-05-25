import pymysql
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import sys
nltk.download('vader_lexicon')
class DatabaseConnector:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor()

    def execute_query(self, query, values=None):
        self.cursor.execute(query, values)

    def commit_changes(self):
        self.connection.commit()

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_sentiment(self, tweet):
        sentiment_scores = self.analyzer.polarity_scores(tweet)
        sentiment_value = sentiment_scores['compound']
        return sentiment_value
    
class TweetProcessor:
    def __init__(self, database_connector, sentiment_analyzer):
        self.database_connector = database_connector
        self.sentiment_analyzer = sentiment_analyzer

    def process_tweets(self, tweets):
        for tweet, tweet_date in tweets:
            sentiment = self.sentiment_analyzer.analyze_sentiment(tweet)

            # Store tweet, date, and sentiment in the database
            query = "INSERT INTO tweets (tweet, tweet_date, sentiment) VALUES (%s, %s, %s)"
            values = (tweet, tweet_date, sentiment)
            self.database_connector.execute_query(query, values)

        self.database_connector.commit_changes()

# MySQL database connection details
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_NAME = 'twitter_sent'

# Create instances of classes
database_connector = DatabaseConnector(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
sentiment_analyzer = SentimentAnalyzer()
tweet_processor = TweetProcessor(database_connector, sentiment_analyzer)

# Connect to the database
database_connector.connect()

# Process mapper output and calculate sentiment
for line in sys.stdin:
    tweet, tweet_date = line.strip().split('\t')
    tweet_processor.process_tweets([(tweet, tweet_date)])

# Close database connection
database_connector.close_connection()
