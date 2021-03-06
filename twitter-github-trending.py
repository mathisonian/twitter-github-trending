import twitter
import os
import sqlitedict
import requests
from bs4 import BeautifulSoup
import time


dbdict = sqlitedict.SqliteDict('tgt.db', autocommit=True)
api = twitter.Api(consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
                  consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
                  access_token_key=os.environ['TWITTER_ACCESS_TOKEN'],
                  access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])



## just make heroku serve something
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello Github Trending!'



## Authenticate to twitter
def tweet(relative_link, description):
    if exists(relative_link):
        print relative_link
        print "link already exists"
        return


    organization = relative_link.split('/')[1]
    name = relative_link.split('/')[2]

    link = "http://github.com" + relative_link

    if description is None:
        description = ''

    description = name + " by " + organization + ": " + description
    if len(description) >= 116:
        description = description[:116-4] + '...'


    description = description.strip()
    tweet_text = description + " " + link

    print "TWEETING: %s" % tweet_text
    api.PostUpdate(tweet_text.strip())
    save(relative_link)
    # don't tweet more than once every 15 minutes
    time.sleep(60 * 15)

def save(key):
    dbdict[key] = True

def exists(key):
    return key in dbdict


def get_trending_repos():
    r = requests.get('https://github.com/trending')
    soup = BeautifulSoup(r.text)
    repositories = soup.find_all("li", { "class" : "repo-leaderboard-list-item" })

    for repo in repositories:
        link = repo.find('a', {"class": "repository-name"})
        description = repo.find('p', {"class": "repo-leaderboard-description" })

        relative_link = link.get('href')
        description_text = None
        if description is not None:
            description_text = description.text

        tweet(link.get('href'), description_text)


def watch_trending():
    while True:
        try:
            get_trending_repos()
        
        # check once every hour
        except Exception, e:
            print e
            pass

        time.sleep(60 * 60)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    watch_trending()
