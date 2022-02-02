import time
import tweepy
import re
import csv
import os
from pandas import DataFrame
import logfileConfig


client_key = ""
client_secret = ""

access_token = ""
access_token_secret = ""

api_key = ""
api_secret = ""

tweets_csv_file_name = "TweetsAndReplies.csv"

logger = logfileConfig.mk_log('TweetRetreival')
last_id_logged = logfileConfig.get_last_tweet_id("process.log",logger)


class CreateTweetsCsv():

    def __init__(self,tweets_csv_file_name,last_id_logged=None) -> None:
        self.tweets_csv_file_name = tweets_csv_file_name
        self.last_id_logged = last_id_logged

    def MakeCsvFile(self) -> bool:
        write_to_file = False
        if os.path.exists(self.tweets_csv_file_name):
            logger.info("Writing to "+self.tweets_csv_file_name+" ....")
            write_to_file=True
        else:
            with open(self.tweets_csv_file_name,"a+") as tweets_csv_file:
                writer = csv.DictWriter(tweets_csv_file,fieldnames=["Tweet","Reply"])
                writer.writeheader()
                logger.info("File created ...\nWriting to "+self.tweets_csv_file_name+" ....")
                write_to_file = True

        print("Writing to file ....")

        return write_to_file

    def GetTweetsAndReplies(self, api):
        regex_str = "@\S*[^\s]|RT |\S*https?:\S*|(\n+)(?=.*)"
        pattern = re.compile(regex_str) 

        if self.MakeCsvFile():
            # Search for a tweet on the timeline
            # Find the replies
            records_added = 0
            for tweet in tweepy.Cursor( api.home_timeline, 
                                        include_rts=True,
                                        since_id = self.last_id_logged,
                                        include_entities=False,
                                        count=200).items():
                replies = tweepy.Cursor(api.search, 
                                        q='to:{} -filter:retweets'.format(tweet.user.screen_name), 
                                        tweet_mode='extended').items(100)

                tweet_data = {"Tweet":[], "Reply":[]}

                try:
                    for reply in replies:
                        if reply.in_reply_to_status_id==tweet.id:
                            tweet_text = pattern.sub('', tweet.text)
                        else:
                            # Find the original tweets for the replies without
                            tweetFetched = api.get_status(reply.in_reply_to_status_id,
                                                            include_entities=False)
                            tweet_text = tweetFetched.text
                            tweet_text = pattern.sub('', tweet_text)
                            
                        reply_text = pattern.sub('', reply.full_text)
                        tweet_data["Tweet"].append(tweet_text)
                        tweet_data["Reply"].append(reply_text)
                    # Combine them all into one df
                    data = DataFrame(tweet_data).drop_duplicates()
                    data.to_csv(self.tweets_csv_file_name,
                            mode = 'a',
                            header = None,
                            index = False)
                    
                    records_added += len(data)
                    
                except tweepy.error.TweepError as er:
                    # Log the specific errors if need be
                    continue

                except Exception as e:
                    logger.exception(e)
   
                time.sleep(3)

            logger.info("Number of entries added : "+str(records_added))
            # Make these the last entry for easy retreival
            id_of_last_tweet= tweet.id  
            logger.info("ID of last retrieved tweet: "+str(id_of_last_tweet))
    

        else:
            logger.critical(" Could Not find/create csv file to write to")



auth = tweepy.OAuthHandler(api_key,api_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(   auth, 
                    wait_on_rate_limit=True, 
                    wait_on_rate_limit_notify=True )

try:
    api.verify_credentials()
    print("twitter_KE_NLP Running")
    make_csv = CreateTweetsCsv( tweets_csv_file_name,
                                last_id_logged=last_id_logged)
    make_csv.GetTweetsAndReplies(api)

except tweepy.error.TweepError as error:
    logger.exception(error)