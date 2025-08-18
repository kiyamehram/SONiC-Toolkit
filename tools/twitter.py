import tweepy
import requests
import json
import re
from datetime import datetime
import argparse
import os
from bs4 import BeautifulSoup
import time
from collections import Counter
import matplotlib.pyplot as plt
import textwrap

class TwitterOSINT:
    def __init__(self, consumer_key=None, consumer_secret=None, username=None, hashtag=None, tweet_url=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.username = username
        self.hashtag = hashtag
        self.tweet_url = tweet_url
        self.api = self._authenticate()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.rate_limit_wait = 15  

    def _authenticate(self):
        if not self.consumer_key or not self.consumer_secret:
            print("Warning: Running in limited mode without API authentication")
            return None
            
        try:
            auth = tweepy.AppAuthHandler(self.consumer_key, self.consumer_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
            print("Authentication successful")
            return api
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return None

    def get_user_profile(self):
        if not self.username:
            return {"error": "Username not provided"}
            
        if not self.api:
            return self._scrape_user_profile()
            
        try:
            user = self.api.get_user(screen_name=self.username)
            profile_data = {
                'username': user.screen_name,
                'name': user.name,
                'id': user.id_str,
                'location': user.location,
                'description': user.description,
                'url': user.url,
                'followers': user.followers_count,
                'following': user.friends_count,
                'tweets': user.statuses_count,
                'created_at': user.created_at.strftime('%Y-%m-%d'),
                'verified': user.verified,
                'profile_image': user.profile_image_url_https.replace('_normal', ''),
                'banner_image': user.profile_banner_url if hasattr(user, 'profile_banner_url') else None,
                'protected': user.protected,
                'default_profile': user.default_profile,
                'analytics': self._analyze_user_tweets()
            }
            
            profile_data['metadata'] = {
                'collection_time': datetime.now().isoformat(),
                'data_source': 'Twitter API',
                'account_age_days': (datetime.now() - user.created_at).days
            }
            
            return profile_data
        except tweepy.TweepError as e:
            return {"error": str(e)}

    def _scrape_user_profile(self):
        try:
            url = f"https://twitter.com/{self.username}"
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            profile_data = {
                'username': self.username,
                'name': soup.find('div', {'data-testid': 'UserName'}).text.split('@')[0].strip(),
                'description': soup.find('div', {'data-testid': 'UserDescription'}).text if soup.find('div', {'data-testid': 'UserDescription'}) else None,
                'metadata': {
                    'collection_time': datetime.now().isoformat(),
                    'data_source': 'Web Scraping',
                    'warning': 'Limited data available without API authentication'
                }
            }
            
            return profile_data
        except Exception as e:
            return {"error": f"Scraping failed: {str(e)}"}

    def _analyze_user_tweets(self, count=200):
        try:
            tweets = self.api.user_timeline(screen_name=self.username, count=count, tweet_mode='extended')
            
            if not tweets:
                return {"warning": "No tweets found or account may be private"}
                
            tweet_data = []
            hashtags = Counter()
            mentions = Counter()
            sources = Counter()
            days = Counter()
            hours = Counter()
            words = Counter()
            
            for tweet in tweets:
                for tag in tweet.entities.get('hashtags', []):
                    hashtags[tag['text'].lower()] += 1
                
                for mention in tweet.entities.get('user_mentions', []):
                    mentions[mention['screen_name'].lower()] += 1
                
                source = re.sub(r'<[^>]+>', '', tweet.source)
                sources[source] += 1
                
                day = tweet.created_at.strftime('%A')
                days[day] += 1
                
                hour = tweet.created_at.strftime('%H:00')
                hours[hour] += 1
                
                text = re.sub(r'https?://\S+', '', tweet.full_text.lower())
                words.update(re.findall(r'\b\w{4,}\b', text))
                
                tweet_data.append({
                    'id': tweet.id_str,
                    'created_at': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'text': tweet.full_text,
                    'likes': tweet.favorite_count,
                    'retweets': tweet.retweet_count,
                    'replies': tweet.reply_count,
                    'hashtags': [tag['text'] for tag in tweet.entities.get('hashtags', [])],
                    'mentions': [mention['screen_name'] for mention in tweet.entities.get('user_mentions', [])],
                    'urls': [url['expanded_url'] for url in tweet.entities.get('urls', [])],
                    'media': self._extract_media(tweet),
                    'source': source
                })
            
            word_cloud = dict(words.most_common(20))
            
            return {
                'tweet_count': len(tweets),
                'most_used_hashtags': dict(hashtags.most_common(10)),
                'most_mentioned_users': dict(mentions.most_common(10)),
                'most_used_words': word_cloud,
                'tweet_sources': dict(sources.most_common()),
                'active_days': dict(days.most_common()),
                'active_hours': dict(hours.most_common()),
                'average_engagement': self._calculate_engagement(tweets),
                'recent_tweets': tweet_data[:5],
                'metadata': {
                    'analysis_period': f"Last {len(tweets)} tweets",
                    'timeframe': f"{tweets[-1].created_at} to {tweets[0].created_at}"
                }
            }
        except tweepy.TweepError as e:
            return {"error": str(e)}

    def _extract_media(self, tweet):
        if 'media' not in tweet.entities:
            return []
            
        return [{
            'url': media['media_url_https'],
            'type': media['type'],
            'display_url': media['display_url']
        } for media in tweet.entities['media']]

    def _calculate_engagement(self, tweets):
        if not tweets:
            return {}
            
        total_likes = sum(t.favorite_count for t in tweets)
        total_retweets = sum(t.retweet_count for t in tweets)
        total_replies = sum(t.reply_count for t in tweets)
        count = len(tweets)
        
        return {
            'avg_likes': round(total_likes/count, 2) if count > 0 else 0,
            'avg_retweets': round(total_retweets/count, 2) if count > 0 else 0,
            'avg_replies': round(total_replies/count, 2) if count > 0 else 0,
            'engagement_rate': round((total_likes + total_retweets + total_replies)/(count * max(1, tweets[0].user.followers_count)) * 100, 4) if count > 0 else 0
        }

    def search_tweets(self, query, count=100):
        if not query:
            return {"error": "Search query not provided"}
            
        if not self.api:
            return {"error": "API authentication required for search"}
            
        try:
            tweets = self.api.search_tweets(q=query, count=count, tweet_mode='extended')
            return [{
                'id': tweet.id_str,
                'created_at': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'text': tweet.full_text,
                'user': tweet.user.screen_name,
                'likes': tweet.favorite_count,
                'retweets': tweet.retweet_count,
                'replies': tweet.reply_count,
                'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}"
            } for tweet in tweets]
        except tweepy.TweepError as e:
            return {"error": str(e)}

    def get_hashtag_info(self):
        if not self.hashtag:
            return {"error": "Hashtag not provided"}
            
        if not self.api:
            return {"error": "API authentication required for hashtag analysis"}
            
        try:
            hashtag = self.hashtag if self.hashtag.startswith('#') else f'#{self.hashtag}'
            tweets = self.api.search_tweets(q=hashtag, count=100, tweet_mode='extended')
            
            users = Counter()
            sources = Counter()
            days = Counter()
            locations = Counter()
            
            for tweet in tweets:
                users[tweet.user.screen_name] += 1
                
                source = re.sub(r'<[^>]+>', '', tweet.source)
                sources[source] += 1
                
                day = tweet.created_at.strftime('%A')
                days[day] += 1
                
                if tweet.user.location:
                    locations[tweet.user.location] += 1
            
            return {
                'hashtag': hashtag,
                'tweet_count': len(tweets),
                'top_users': dict(users.most_common(10)),
                'tweet_sources': dict(sources.most_common()),
                'active_days': dict(days.most_common()),
                'common_locations': dict(locations.most_common(5)),
                'sample_tweets': [{
                    'id': tweet.id_str,
                    'text': tweet.full_text,
                    'user': tweet.user.screen_name,
                    'created_at': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}"
                } for tweet in tweets[:5]],
                'metadata': {
                    'timeframe': f"Recent {len(tweets)} tweets",
                    'collection_time': datetime.now().isoformat()
                }
            }
        except tweepy.TweepError as e:
            return {"error": str(e)}

    def get_tweet_info(self):
        if not self.tweet_url:
            return {"error": "Tweet URL not provided"}
            
        try:
            tweet_id = re.search(r'/status/(\d+)', self.tweet_url).group(1)
            
            if not self.api:
                return self._scrape_tweet_info(tweet_id)
                
            tweet = self.api.get_status(tweet_id, tweet_mode='extended')
            
            result = {
                'id': tweet.id_str,
                'created_at': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'text': tweet.full_text,
                'user': tweet.user.screen_name,
                'likes': tweet.favorite_count,
                'retweets': tweet.retweet_count,
                'replies': tweet.reply_count,
                'hashtags': [tag['text'] for tag in tweet.entities.get('hashtags', [])],
                'mentions': [mention['screen_name'] for mention in tweet.entities.get('user_mentions', [])],
                'urls': [url['expanded_url'] for url in tweet.entities.get('urls', [])],
                'media': self._extract_media(tweet) if 'media' in tweet.entities else [],
                'source': re.sub(r'<[^>]+>', '', tweet.source),
                'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}",
                'conversation_analysis': self._analyze_conversation(tweet),
                'metadata': {
                    'collection_time': datetime.now().isoformat(),
                    'data_source': 'Twitter API'
                }
            }
            
            result['sentiment'] = self._analyze_sentiment(tweet.full_text)
            
            return result
        except tweepy.TweepError as e:
            return {"error": str(e)}

    def _scrape_tweet_info(self, tweet_id):
        try:
            url = f"https://twitter.com/i/web/status/{tweet_id}"
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            tweet_text = soup.find('div', {'data-testid': 'tweetText'}).text if soup.find('div', {'data-testid': 'tweetText'}) else "Not available"
            
            return {
                'id': tweet_id,
                'text': tweet_text,
                'url': url,
                'metadata': {
                    'collection_time': datetime.now().isoformat(),
                    'data_source': 'Web Scraping',
                    'warning': 'Limited data available without API authentication'
                }
            }
        except Exception as e:
            return {"error": f"Scraping failed: {str(e)}"}

    def _analyze_conversation(self, tweet):
        if not self.api:
            return {"warning": "API required for conversation analysis"}
            
        try:
            replies = tweepy.Cursor(self.api.search_tweets, q=f"to:{tweet.user.screen_name}", since_id=tweet.id_str, tweet_mode='extended').items(50)
            
            participants = Counter()
            sentiment = {'positive': 0, 'neutral': 0, 'negative': 0}
            
            for reply in replies:
                if reply.in_reply_to_status_id_str == tweet.id_str:
                    participants[reply.user.screen_name] += 1
                    text = reply.full_text.lower()
                    if any(word in text for word in ['great', 'awesome', 'love', 'like', '👍', '❤️']):
                        sentiment['positive'] += 1
                    elif any(word in text for word in ['bad', 'hate', 'stupid', 'worst', '👎']):
                        sentiment['negative'] += 1
                    else:
                        sentiment['neutral'] += 1
            
            return {
                'reply_count': sum(participants.values()),
                'unique_participants': len(participants),
                'top_commenters': dict(participants.most_common(3)),
                'sentiment': sentiment
            }
        except tweepy.TweepError as e:
            return {"error": str(e)}

    def _analyze_sentiment(self, text):
        positive_words = ['good', 'great', 'excellent', 'awesome', 'happy']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'angry']
        
        text = text.lower()
        positive = sum(1 for word in positive_words if word in text)
        negative = sum(1 for word in negative_words if word in text)
        
        if positive > negative:
            return 'positive'
        elif negative > positive:
            return 'negative'
        else:
            return 'neutral'

    def get_user_connections(self):
        if not self.username:
            return {"error": "Username not provided"}
            
        if not self.api:
            return {"error": "API authentication required for connection analysis"}
            
        try:
            followers = self.api.get_follower_ids(screen_name=self.username)
            following = self.api.get_friend_ids(screen_name=self.username)
            
            return {
                'followers_count': len(followers),
                'following_count': len(following),
                'mutual_connections': len(set(followers).intersection(set(following))),
                'followers_sample': [str(id) for id in followers[:5]],
                'following_sample': [str(id) for id in following[:5]],
                'metadata': {
                    'collection_time': datetime.now().isoformat(),
                    'warning': 'Due to API limitations, only IDs are available for connections'
                }
            }
        except tweepy.TweepError as e:
            return {"error": str(e)}

    def generate_report(self, data, filename="twitter_osint_report"):
        try:
            json_file = f"{filename}.json"
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=4)
            
            txt_file = f"{filename}.txt"
            with open(txt_file, 'w') as f:
                f.write("="*50 + "\n")
                f.write("Twitter OSINT Report\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                
                if 'user_profile' in data:
                    profile = data['user_profile']
                    f.write(f"User Profile: @{profile.get('username', 'N/A')}\n")
                    f.write(f"Name: {profile.get('name', 'N/A')}\n")
                    f.write(f"Bio: {textwrap.fill(profile.get('description', 'N/A'), width=80)}\n")
                    f.write(f"Followers: {profile.get('followers', 'N/A'):,}\n")
                    f.write(f"Following: {profile.get('following', 'N/A'):,}\n")
                    f.write(f"Tweets: {profile.get('tweets', 'N/A'):,}\n")
                    f.write(f"Account created: {profile.get('created_at', 'N/A')}\n")
                    f.write(f"Verified: {'Yes' if profile.get('verified') else 'No'}\n")
                    f.write("\n")
                    
                if 'hashtag_info' in data:
                    hashtag = data['hashtag_info']
                    f.write(f"Hashtag Analysis: {hashtag.get('hashtag', 'N/A')}\n")
                    f.write(f"Total tweets analyzed: {hashtag.get('tweet_count', 'N/A')}\n")
                    f.write("\nTop Users:\n")
                    for user, count in hashtag.get('top_users', {}).items():
                        f.write(f"- @{user}: {count} tweets\n")
                    f.write("\n")
                    
            print(f"Report generated: {json_file}, {txt_file}")
            return {"success": True, "files": [json_file, txt_file]}
        except Exception as e:
            return {"error": str(e)}

def print_banner():
    print("""
████████╗██╗    ██╗██╗████████╗████████╗███████╗██████╗ 
╚══██╔══╝██║    ██║██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗
   ██║   ██║ █╗ ██║██║   ██║      ██║   █████╗  ██████╔╝
   ██║   ██║███╗██║██║   ██║      ██║   ██╔══╝  ██╔══██╗
   ██║   ╚███╔███╔╝██║   ██║      ██║   ███████╗██║  ██║
   ╚═╝    ╚══╝╚══╝ ╚═╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝
                                                        
Twitter OSINT Tool v1.0
""")

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="Twitter OSINT Tool")
    parser.add_argument("-k", "--consumer_key", help="Twitter API consumer key", default=os.getenv('TWITTER_CONSUMER_KEY'))
    parser.add_argument("-s", "--consumer_secret", help="Twitter API consumer secret", default=os.getenv('TWITTER_CONSUMER_SECRET'))
    parser.add_argument("-u", "--username", help="Twitter username to investigate")
    parser.add_argument("-ht", "--hashtag", help="Hashtag to analyze")
    parser.add_argument("-t", "--tweet_url", help="Tweet URL to analyze")
    parser.add_argument("-q", "--query", help="Search query for tweets")
    parser.add_argument("-o", "--output", help="Output file name (without extension)")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive report")
    
    args = parser.parse_args()
    
    if not any([args.username, args.hashtag, args.tweet_url, args.query]):
        parser.print_help()
        return
    
    osint = TwitterOSINT(
        consumer_key=args.consumer_key,
        consumer_secret=args.consumer_secret,
        username=args.username,
        hashtag=args.hashtag,
        tweet_url=args.tweet_url
    )
    
    results = {}
    
    if args.username:
        print(f"[*] Collecting data for user: @{args.username}")
        results["user_profile"] = osint.get_user_profile()
        results["user_connections"] = osint.get_user_connections()
    
    if args.hashtag:
        print(f"[*] Analyzing hashtag: {args.hashtag}")
        results["hashtag_info"] = osint.get_hashtag_info()
    
    if args.tweet_url:
        print(f"[*] Extracting tweet data from: {args.tweet_url}")
        results["tweet_info"] = osint.get_tweet_info()
    
    if args.query:
        print(f"[*] Searching for tweets with query: {args.query}")
        results["tweet_search"] = osint.search_tweets(args.query)
    
    if args.report:
        output_name = args.output if args.output else "twitter_osint_report"
        report_result = osint.generate_report(results, output_name)
        print(json.dumps(report_result, indent=2))
    else:
        print(json.dumps(results, indent=2))
        
        if args.output:
            with open(f"{args.output}.json", 'w') as f:
                json.dump(results, f, indent=4)
            print(f"\nResults saved to {args.output}.json")

if __name__ == "__main__":
    main()