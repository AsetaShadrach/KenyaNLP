import logfileConfig
from GetTweets import CreateTweetsCsv, tweepy

client_key = ""
client_secret = ""

access_token = ""
access_token_secret = ""

api_key = ""
api_secret = ""


tweets_csv_file_path = "data/TweetsAndReplies.csv"

def main(api_key, api_secret,access_token, access_token_secret ):
    '''
    Combine everything and run it :
    From csv/log file creation, to the appending of data and logging
    '''
    logger = logfileConfig.mk_log('TweetRetreival')
    last_id_logged = logfileConfig.get_last_tweet_id("process.log",logger)

    auth = tweepy.OAuthHandler(api_key,api_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(   auth, 
                        wait_on_rate_limit=True, 
                        wait_on_rate_limit_notify=True )

    try:
        api.verify_credentials()
        print("twitter_KE_NLP Running")
        make_csv = CreateTweetsCsv( tweets_csv_file_path,
                                    logger,
                                    last_id_logged=last_id_logged)
        make_csv.GetTweetsAndReplies(api)

    except Exception as error:
        logger.exception(error)
        logger.info("ID of last retrieved tweet before the Error above: "+str(last_id_logged ))
    
    return None


if __name__ == '__main__':
    main(api_key, api_secret,access_token, access_token_secret )