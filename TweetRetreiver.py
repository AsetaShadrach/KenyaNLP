import logfileConfig
from GetTweets import CreateTweetsCsv, tweepy


def main(api_key, api_secret,access_token, access_token_secret,tweets_csv_file_path ):
    '''
    Combine everything and run it :
    From csv/log file creation, to the appending of data and logging
    '''
    logger = logfileConfig.mk_log('TweetRetreival')
    last_id_logged = logfileConfig.get_last_tweet_id("process.log",logger)

    try:
        auth = tweepy.OAuthHandler(api_key,api_secret)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(   auth, 
                            wait_on_rate_limit=True, 
                            wait_on_rate_limit_notify=True )

    
        api.verify_credentials()
        logger.info("twitter_KE_NLP Running")
        print("twitter_KE_NLP Running")
        
        tweet_cursor  = tweepy.Cursor( api.home_timeline, 
                                            include_rts=True, 
                                            since_id = last_id_logged,
                                            include_entities=False,
                                            count=200)

        make_csv = CreateTweetsCsv( tweets_csv_file_path,
                                    logger,
                                    tweet_cursor,
                                    last_id_logged=last_id_logged)

        make_csv.GetTweetsAndReplies(api)

    
    except Exception as error:
        logger.exception(error)
        # Check if the connection already existed and if it has run atleast one cycle
        if make_csv and make_csv.current_since_id :
            logger.info("Number of entries added before the Error above: "+str(make_csv.records_added))
            logger.info("ID of last retrieved tweet before the Error above: "+str(make_csv.current_since_id ))
        else:
            logger.info("Number of entries added before the Error above: "+str(0))
            logger.info("ID of last retrieved tweet before the Error above: "+str(last_id_logged ))
    

    return None
    

if __name__ == '__main__':
    client_key = ""
    client_secret = ""

    access_token = ""
    access_token_secret = ""

    api_key = ""
    api_secret = ""


    tweets_csv_file_path = "data/TweetsAndReplies.csv"

    main(api_key, api_secret,access_token, access_token_secret, tweets_csv_file_path )