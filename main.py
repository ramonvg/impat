import tweepy
import sqlite3
import os

from pathlib import Path

db = sqlite3.connect('impat.db')
PLACEHOLDER = "{{%TWEET_ID%}}"


def init_db():
    cursor = db.cursor()
    cursor.execute(
        """
    CREATE TABLE tweets(id TEXT  PRIMARY KEY, timestamp INT);
    """
    )


def import_tweets(screen_name):
    auth = tweepy.OAuthHandler(
        os.environ["CONSUMER_KEY"], os.environ["CONSUMER_SECRET"]
    )
    auth.set_access_token(os.environ["ACCESS_KEY"], os.environ["ACCESS_SECRET"])
    api = tweepy.API(auth)

    new_tweets = api.user_timeline(screen_name=screen_name, count=200)
    new_tweets = (
        x
        for x in new_tweets
        if "informativo matinal para ahorrar tiempo" in x.text.lower()
    )
    cursor = db.cursor()
    for tweet in new_tweets:
        cursor.execute(
            "INSERT OR IGNORE INTO tweets (id, timestamp) VALUES (?, ?)",
            (tweet.id, tweet.created_at.timestamp()),
        )
    db.commit()


def render_html():
    cursor = db.cursor()
    (last_id,) = cursor.execute(
        "SELECT id FROM tweets ORDER BY timestamp DESC LIMIT 1"
    ).fetchone()
    template = (Path() / "index.template").read_text()
    result = template.replace(PLACEHOLDER, last_id)
    with open("index.html", "w") as output:
        output.write(result)


if __name__ == '__main__':
    import_tweets("angelmartin_nc")
    render_html()
