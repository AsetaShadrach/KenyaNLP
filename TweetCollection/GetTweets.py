import tweepy
import re
import csv
import os
import sys
from pandas import DataFrame

class CreateTweetsCsv():

    def __init__(self,tweets_csv_file_path,logger,tweet_cursor,last_id_logged=None) -> None:
        self.tweets_csv_file_path = tweets_csv_file_path
        self.logger = logger
        self.last_id_logged = last_id_logged
        self.tweet_cursor =  tweet_cursor

    def MakeCsvFile(self) -> bool:
        write_to_file = False
        if os.path.exists(self.tweets_csv_file_path):
            self.logger.info("Writing to file(s) ....")
            write_to_file=True
        else:
            with open(self.tweets_csv_file_path,"a+") as tweets_csv_file:
                writer = csv.DictWriter(tweets_csv_file,fieldnames=["Tweet","Reply"])
                writer.writeheader()
                self.logger.info("File created ...\nWriting to file(s) ....")
                write_to_file = True

        print("Writing to file(s) ....")

        return write_to_file

    def GetTweetsAndReplies(self, api, use_keywords=None):
        regex_str = "@\S*[^\s]|RT |\S*https?:\S*|(\n+)(?=.*)"
        pattern = re.compile(regex_str) 

        if self.MakeCsvFile():
            # Search for a tweet on the timeline
            # Find the replies
            try:
                self.records_added = 0
                self.current_since_id,tweet_text,reply_text= None,None,None
                # Alter the number of items to be returned
                for tweet in self.tweet_cursor.items():

                    if use_keywords:
                        replies = tweepy.Cursor(api.search,
                                                q='to:{} -filter:retweets'.format(tweet.user.screen_name),
                                                tweet_mode='extended').items(10)

                    else:
                        replies = tweepy.Cursor(api.search,
                                                tweet_mode='extended',
                                                q='to:{} -filter:retweets'.format(tweet.user.screen_name),
                                                include_entities=False).items(100)


                    tweet_data = {"Tweet":[], "Reply":[]}

                    try:
                        for reply in replies:
                            if reply.in_reply_to_status_id==tweet.id:
                                # use full_text instead of text because of tweet mode extend
                                tweet_text = pattern.sub('', tweet.full_text)
                            else:
                                if reply.in_reply_to_status_id != None:
                                # Find the original tweets for the replies without
                                    tweetFetched = api.get_status(reply.in_reply_to_status_id,
                                                                    include_entities=False)
                                    tweet_text = tweetFetched.text
                                    tweet_text = pattern.sub('', tweet_text)
                                
                            reply_text = pattern.sub('', reply.full_text)
                            if (tweet_text != None) & (reply_text != None):
                                tweet_data["Tweet"].append(tweet_text)
                                tweet_data["Reply"].append(reply_text)
                        # Combine them all into one df
                        data = DataFrame(tweet_data).drop_duplicates()
                        data.to_csv(self.tweets_csv_file_path,
                                mode = 'a',
                                header = None,
                                index = False)
                        
                        # Get the amount of data recieved
                        self.records_added += len(data)
                        # Save the last tweet id retreived
                        self.current_since_id = tweet.id


                    except tweepy.error.TweepError as er:
                        # Log the specific errors if need be
                        self.logger.error("TWEEPY ERROR: ",er)
                        continue
                    
                    except Exception as e:
                        self.logger.exception(e)
                        self.logger.info("Number of entries added : "+str(self.records_added))
                        if self.current_since_id:
                            self.logger.info("ID of last retrieved tweet before the error above: "+str(self.current_since_id ))
                        else:
                            # If it hasn't completed the loop successfully even once
                            self.logger.info("ID of last retrieved tweet before the error above: "+str(self.last_id_logged ))


                self.logger.info("Number of entries added : "+str(self.records_added))
                # Make these the last entry for easy retreival 
                self.logger.info("ID of last retrieved tweet: "+str(self.current_since_id ))

            except KeyboardInterrupt:
                # These will log the last values assigned before the interrupt
                self.logger.info("Number of entries added before KeybordInterrupt: "+str(self.records_added))
                
                # if it had run through a complete cycle for tweet replies at least once
                if self.current_since_id:
                    self.logger.info("ID of last retrieved tweet before KeybordInterrupt: "+str(self.current_since_id ))
                else:
                    # If it hasn't completed the loop successfully even once
                    self.logger.info("ID of last retrieved tweet before KeybordInterrupt: "+str(self.last_id_logged ))
                      
                
                sys.exit(0)


        else:
            self.logger.critical(" Could Not find/create csv file to write to")
        
 