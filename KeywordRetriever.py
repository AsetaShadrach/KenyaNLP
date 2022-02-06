import logfileConfig
from GetTweets import CreateTweetsCsv, tweepy


def main(api_key, api_secret, access_token, access_token_secret):
    logger = logfileConfig.mk_log('KeywordRetrieval')

    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    try:
        api.verify_credentials()
        logger.info("twitter_KE_NLP Running")

        for keyword_ in ['njaanuary', 'expressway', 'construction', 'mejja', 'masculinitysaturday']:
            tweets_csv_file_path = f"Keyword_{keyword_}_AndReplies.csv"

            make_csv = CreateTweetsCsv(tweets_csv_file_path,
                                       logger)
            make_csv.GetTweetsByKeyword(api, kword=keyword_)

    except Exception as error:
        logger.exception(error)

    return None


if __name__ == '__main__':
    main(api_key, api_secret, access_token, access_token_secret)
