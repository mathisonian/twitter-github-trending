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


## Authenticate to twitter
def tweet(relative_link, description):
    if exists(relative_link):
        print relative_link
        print "link already exists"
        return


    organization = relative_link.split('/')[1]
    name = relative_link.split('/')[2]

    # don't tweet more than once every 5 minutes
    link = "http://github.com" + relative_link

    if description is None:
        description = ''

    description = name + " by " + organization + ": " + description
    if len(description) > 120:
        description = description[:116] + '...'    


    tweet_text = description + " " + link

    print "TWEETING: %s" % tweet_text
    api.PostUpdate(tweet_text.strip())
    save(relative_link)
    time.sleep(60 * 5)

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
        get_trending_repos()
        
        # check once every hour
        time.sleep(60 * 60)


if __name__ == "__main__":
    watch_trending()
