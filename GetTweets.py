import time
import tweepy
import re
import csv
import os
import sys
from pandas import DataFrame

class CreateTweetsCsv():

    def __init__(self,tweets_csv_file_path,logger,last_id_logged=None) -> None:
        self.tweets_csv_file_path = tweets_csv_file_path
        self.logger = logger
        self.last_id_logged = last_id_logged

    def MakeCsvFile(self) -> bool:
        write_to_file = False
        if os.path.exists(self.tweets_csv_file_path):
            self.logger.info("Writing to "+self.tweets_csv_file_path+" ....")
            write_to_file=True
        else:
            with open(self.tweets_csv_file_path,"a+") as tweets_csv_file:
                writer = csv.DictWriter(tweets_csv_file,fieldnames=["Tweet","Reply"])
                writer.writeheader()
                self.logger.info("File created ...\nWriting to "+self.tweets_csv_file_path+" ....")
                write_to_file = True

        print("Writing to file ....")

        return write_to_file

    def GetTweetsAndReplies(self, api):
        regex_str = "@\S*[^\s]|RT |\S*https?:\S*|(\n+)(?=.*)"
        pattern = re.compile(regex_str) 

        if self.MakeCsvFile():
            # Search for a tweet on the timeline
            # Find the replies
            try:
                records_added = 0
                for tweet in tweepy.Cursor( api.home_timeline, 
                                            include_rts=True,
                                            since_id = self.last_id_logged,
                                            include_entities=False,
                                            count=200).items():
                    replies = tweepy.Cursor(api.search, 
                                            q='to:{} -filter:retweets'.format(tweet.user.screen_name), 
                                            tweet_mode='extended', 
                                            include_entities=False).items(100)

                    tweet_data = {"Tweet":[], "Reply":[]}

                    try:
                        data_saved = False
                        for reply in replies:
                            if reply.in_reply_to_status_id==tweet.id:
                                tweet_text = pattern.sub('', tweet.text)
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
                        
                        # Save the last tweet id retreived
                        current_since_id = tweet.id
                        # Get the amount of data recieved
                        records_added += len(data)
                        # We will use this to check if saving was complete before interrupt interrupts
                        data_saved = True
                        
                    except tweepy.error.TweepError as er:
                        # Log the specific errors if need be
                        continue
                    
                    except Exception as e:
                        self.logger.exception(e)

    
                    time.sleep(3)

                self.logger.info("Number of entries added : "+str(records_added))
                # Make these the last entry for easy retrieval
                self.logger.info("ID of last retrieved tweet: "+str(tweet.id ))
            except KeyboardInterrupt:
                if data_saved:
                    # These will log the last values assigned before the interrupt
                    self.logger.info("Number of entries added before KeyboardInterrupt: "+str(records_added))
                    if current_since_id:
                        self.logger.info("ID of last retrieved tweet before KeyboardInterrupt: "+str(current_since_id ))
                    else:
                        # If it hasn't completed the loop successfully even once
                        self.logger.info("ID of last retrieved tweet before KeyboardInterrupt: "+str(self.last_id_logged ))
                        
                else:
                    # If the data was
                    self.logger.info("ID of last retrieved tweet before KeyboardInterrupt: "+str(self.last_id_logged ))
                
                sys.exit(0)


        else:
            self.logger.critical(" Could Not find/create csv file to write to")



    def GetTweetsByKeyword(self, api, kword):
        regex_str = "@\S*[^\s]|RT |\S*https?:\S*|(\n+)(?=.*)"
        pattern = re.compile(regex_str)

        if self.MakeCsvFile():
            # Search for a tweet on the timeline
            # Find the replies
            for tweet in tweepy.Cursor(api.search,
                                       q=kword).items():
                replies = tweepy.Cursor(api.search,
                                        q='to:{} -filter:retweets'.format(tweet.user.screen_name),
                                        tweet_mode='extended').items(50)

                tweet_data = {"Tweet": [], "Reply": []}

                try:
                    for reply in replies:
                        if reply.in_reply_to_status_id == tweet.id:
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
                    data.to_csv(self.tweets_csv_file_path,
                                mode='a',
                                header=None,
                                index=False)

                    self.logger.info("Data Entered: ", len(data))

                except:
                    time.sleep(120)
                    continue


        else:
            self.logger.critical(" Could Not find/create csv file to write to")
        
        

