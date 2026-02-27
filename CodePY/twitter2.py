from twikit import Client, TooManyRequests
import csv
import asyncio
from datetime import datetime
from random import randint
import re
import os

# === CONFIG ===
MINIMUM_TWEETS = 150000  # Number of new tweets to fetch per run

# Run one at a time by uncommenting
# --- For Nov 2020 Election ---
# QUERY = '(#MAGA OR #Trump2024 OR #BlueWave OR #StopTheSteal OR #ElectionFraud OR Trump OR Biden) lang:en until:2020-11-30 since:2020-10-15'
# CSV_FILE = 'election2020_tweets.csv'

# --- For Nov 2024 Election ---
QUERY = '(#UofU OR #UtahCampus OR #utahshooters OR #UtahStudents OR #CampusLife OR #CollegeSafety OR #CampusNews OR #Utah OR #UniversityOfUtah OR #GunViolence OR #CampusShootings OR #GunControl OR #ActiveShooter OR #SLCPD OR #UtahShooting OR #ShootingUtah OR #ShootingAtUtah OR #CampusSafety OR #GunViolence OR #UTPolice OR #CharlieKirk OR #TurningPointUSA OR #charliekirk11 OR #TPUSA) lang:en until:2025-09-30 since:2025-08-01'
CSV_FILE = 'Utah_tweets2.csv'

PRODUCT = 'Latest'  # Can also try 'Mixed'

# === LOAD EXISTING DATA ===
seen_ids = set()
total_tweet_counter = 0
file_exists = os.path.isfile(CSV_FILE)

if file_exists:
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if row:
                seen_ids.add(row[0])  # Tweet ID is first column
                total_tweet_counter += 1

# Start session-specific counter
new_tweet_counter = 0

# === CREATE FILE IF NEEDED ===
with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow([
            'Tweet ID', 'Tweet_count', 'Username', 'Text', 'Created At', 'Retweets', 'Likes',
            'User Bio', 'Follower Count', 'Following Count',
            'Replies', 'Location', 'Age', 'Gender', 'Hashtags'
        ])


# === FUNCTION TO FETCH TWEETS ===
async def get_tweets(tweets, client):
    if tweets is None:
        print(f'{datetime.now()} - Getting tweets...')
        tweets = await client.search_tweet(QUERY, product=PRODUCT)
    else:
        wait_time = randint(5, 10)
        print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds ...')
        await asyncio.sleep(wait_time)
        tweets = await tweets.next()
    return tweets


# === MAIN FUNCTION ===
async def main():
    global new_tweet_counter, total_tweet_counter
    client = Client(language='en-US')
    client.load_cookies('cookies1.json')

    tweets = None

    while new_tweet_counter < MINIMUM_TWEETS:
        try:
            tweets = await get_tweets(tweets, client)
        except TooManyRequests as e:
            rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
            print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
            wait_time = (rate_limit_reset - datetime.now()).total_seconds()
            await asyncio.sleep(wait_time)
            continue

        if not tweets:
            print(f'{datetime.now()} - No more tweets found. Ending this run.')
            break

        for tweet in tweets:
            tweet_id = str(tweet.id)
            if tweet_id in seen_ids:
                continue

            seen_ids.add(tweet_id)
            new_tweet_counter += 1
            total_tweet_counter += 1

            username = tweet.user.name
            text = tweet.full_text
            created_at = tweet.created_at
            retweets = tweet.retweet_count
            likes = tweet.favorite_count
            user_bio = tweet.user.description
            follower_count = tweet.user.followers_count
            following_count = tweet.user.following_count
            replies = tweet.reply_count
            location = tweet.user.location if tweet.user.location else "Unknown"
            hashtags = re.findall(r"#(\w+)", text)
        
            age = "Unknown"
            gender = "Unknown"

            with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    tweet_id, total_tweet_counter, username, text, created_at, retweets, likes,
                    user_bio, follower_count, following_count,
                    replies, location, age, gender, hashtags
                ])

            if new_tweet_counter >= MINIMUM_TWEETS:
                break

        print(f'{datetime.now()} - Collected {new_tweet_counter} new tweets so far.')

    print(f'{datetime.now()} - Run complete. Total tweets in CSV: {total_tweet_counter}')


# === RUN SCRIPT ===
if __name__ == "__main__":
    asyncio.run(main())