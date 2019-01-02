import configparser
from requests_oauthlib import OAuth1Session
import api.tweet_messages as tweet_messages
import db.db as db

config = configparser.ConfigParser()
config.read('api/twitter_conf.ini')
CK = config['DEFAULT']['CONSUMER_KEY']
CS = config['DEFAULT']['CONSUMER_SECRET']
AT = config['DEFAULT']['ACCESS_TOKEN']
ATS = config['DEFAULT']['ACCESS_TOKEN_SECRET']

def tweet(action, feeling, info):
    session = OAuth1Session(CK, CS, AT, ATS)
    url = 'https://api.twitter.com/1.1/statuses/update.json'
    message = tweet_messages.get_message(action)
    kaomoji = tweet_messages.get_kaomoji(feeling)
    tags = "#USDJPY #FX"
    content = (
        message + kaomoji + "\n"
        + "\n".join(info) + "\n"
        + tags
    )
    params = {
        'status': content
    }
    db.write_log('twitter_api', 'content: ' + content)

    done = False
    retry = 0
    max_retry = 2
    while (not done) and (retry <= max_retry):
        try:
            response = session.post(url, params=params)
            if response.status_code != 200:
                raise Exception('tweet failed')
            else:
                db.write_log('twitter_api', 'tweet scceeded')
                done = True
        except Exception as e:
            db.write_log('exception', str(e))
            continue
        finally:
            retry +=1
