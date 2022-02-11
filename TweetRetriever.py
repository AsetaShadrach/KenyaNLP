import logfileConfig
from GetTweets import CreateTweetsCsv, tweepy


def main(api_key, api_secret, access_token, access_token_secret,
         tweets_csv_file_path=None, list_of_keywords=None, to_run='tweet'):

    logger = logfileConfig.mk_log('KeywordRetrieval')
    last_id_logged = logfileConfig.get_last_tweet_id("process.log",logger)
    make_csv = None

    try:
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth,
                        wait_on_rate_limit=True,
                        wait_on_rate_limit_notify=True)

        api.verify_credentials()
        logger.info("twitter_KE_NLP Running")
        print("twitter_KE_NLP Running")

        if to_run == 'keyword':

            for keyword_ in list_of_keywords:
                tweets_csv_file_path = f"Keyword_{keyword_}_AndReplies.csv"
                # Allows for use of different cursors
                tweet_cursor = tweepy.Cursor(api.search,
                                        q=keyword_)

                make_csv = CreateTweetsCsv(tweets_csv_file_path,
                                        logger,
                                        tweet_cursor)

                make_csv.GetTweetsAndReplies(api, use_keywords=True)

        else:

            tweet_cursor = tweepy.Cursor(api.home_timeline,
                                         include_rts=True,
                                         since_id=last_id_logged,
                                         include_entities=False,
                                         count=200)

            make_csv = CreateTweetsCsv(tweets_csv_file_path,
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


    access_token = ""
    access_token_secret = ""

    api_key = ""
    api_secret = ""


    to_run = 'keyword'

    tweets_csv_file_path = "c:/Users/Aseta/Desktop/D S/ML_AI/Twitter app/TweetsAndReplies.csv"

    list_of_keywords = ['njaanuary', 'expressway', 'construction', 'mejja', 'masculinitysaturday']
    

    # for keywords
    '''
    main(api_key, api_secret, access_token, access_token_secret,
         list_of_keywords=list_of_keywords, to_run=to_run)'''

    # for general tweets
    main(api_key, api_secret, access_token, access_token_secret,
         tweets_csv_file_path=tweets_csv_file_path)
