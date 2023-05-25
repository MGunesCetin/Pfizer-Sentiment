import requests
import base64
import json

class TwitterScraper:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.base_url = "https://api.twitter.com/1.1/search/tweets.json"
        self.auth_token = self.get_auth_token(consumer_key, consumer_secret, access_token, access_token_secret)

    def get_auth_token(self, consumer_key, consumer_secret, access_token, access_token_secret):
        key_secret = '{}:{}'.format(consumer_key, consumer_secret).encode('ascii')
        b64_encoded_key = base64.b64encode(key_secret).decode('ascii')

        auth_url = 'https://api.twitter.com/oauth2/token'
        auth_headers = {
            'Authorization': 'Basic {}'.format(b64_encoded_key),
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }
        auth_data = {'grant_type': 'client_credentials'}

        auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)
        auth_resp_data = auth_resp.json()
        auth_token = auth_resp_data['access_token']
        return auth_token

    def get_tweets(self, date, topic):
        params = {
            "q": topic,
            "count": 100,
            "result_type": "recent",
            "until": date
        }
        headers = {
            'Authorization': 'Bearer {}'.format(self.auth_token)
        }

        all_tweets = []
        max_tweets = 200
        while len(all_tweets) < max_tweets:
            response = requests.get(self.base_url, params=params, headers=headers)
            data = response.json()

            tweets = data.get("statuses", [])
            all_tweets.extend(tweets)

            if "next_results" not in data.get("search_metadata", {}):
                break

            next_results = data["search_metadata"]["next_results"]
            params = dict(x.strip().split('=') for x in next_results[1:].split("&"))

        return all_tweets[:max_tweets]


# Example usage
access_token= '358138140-mwHh89hZAvtpnYknXUFmuntAZJFdFvvEFc0sdv5R'
access_token_secret = '2tFE2l46VqEKbtciXakCxOc12ByX8j8oOfjuj8zeOO5KH'
consumer_key= 'UugW7t0OUYczGoBBHrN33YXAT'
consumer_secret = 'WtbLz0peBbvwk49uUR7kVi5SGnYUEKhNoJ6Njai6lHzCf7qvl5'

scraper = TwitterScraper(consumer_key, consumer_secret, access_token, access_token_secret)
tweets = scraper.get_tweets("2022-05-19", "Python")
for tweet in tweets:
    print(tweet["text"])
