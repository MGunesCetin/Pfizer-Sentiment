import pymysql
from datetime import datetime, timedelta
from TwitterScraper import TwitterScraper



# Twitter API credentials
CONSUMER_KEY = 'UugW7t0OUYczGoBBHrN33YXAT'
CONSUMER_SECRET = 'WtbLz0peBbvwk49uUR7kVi5SGnYUEKhNoJ6Njai6lHzCf7qvl5'
ACCESS_TOKEN =  '358138140-mwHh89hZAvtpnYknXUFmuntAZJFdFvvEFc0sdv5R'
ACCESS_TOKEN_SECRET = '2tFE2l46VqEKbtciXakCxOc12ByX8j8oOfjuj8zeOO5KH'

# Get date range for last 24 months
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=30 * 1)).strftime('%Y-%m-%d')

# Initialize TwitterScraper
scraper = TwitterScraper(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)


# Execute Twitter search and store in MySQL database
max_tweets_per_day = 200
tweets_per_day = {}
tweets = scraper.get_tweets(start_date, end_date, "Pfizer")
for tweet in tweets:
    tweet_text = tweet["text"]
    tweet_date = datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y').strftime('%Y-%m-%d')

    # Check tweet count for the current day
    if tweet_date not in tweets_per_day:
        tweets_per_day[tweet_date] = 1
    else:
        tweets_per_day[tweet_date] += 1

    # Store tweet and date if tweet count for the day is within the limit
    if tweets_per_day[tweet_date] <= max_tweets_per_day:
        # Print tweet and date
        print(f"{tweet_text}\t{tweet_date}")


