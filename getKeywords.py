import time
import tweepy
import re
import csv
import os
from pandas import DataFrame


#client_key = ""
#client_secret = ""


access_token = "906869845958053888-TpqjV7r9ATZihNFGfVw5v5OMIRbEhDR"
access_token_secret = "FKoLtt63BahUnhNGKA7snlHzQVXp1jsgWwF9JZmEKI628"

api_key = "KHBNHJaqjR2zWKhQp6l6uBOPg"
api_secret = "tgDESoMJp3je8x5UckTyrA1SdT0ISQoYRyqJWddL3dTRVPvxXF"

tweets_csv_file_name = "KeywordsAndReplies.csv"


class CreateTweetsCsv():

    def __init__(self,tweets_csv_file_name) -> None:
        self.tweets_csv_file_name = tweets_csv_file_name

    def MakeCsvFile(self) -> bool:
        write_to_file = False
        if os.path.exists(self.tweets_csv_file_name):
            print("Writing to "+self.tweets_csv_file_name+" ....")
            write_to_file=True
        else:
            with open(self.tweets_csv_file_name,"a+") as tweets_csv_file:
                writer = csv.DictWriter(tweets_csv_file,fieldnames=["Tweet","Reply"])
                writer.writeheader()
                print("File created ...\nWriting to "+self.tweets_csv_file_name+" ....")
                write_to_file = True

        return write_to_file

    def GetTweetsAndReplies(self, api, kword):
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
                    
                    print("Data Entered ",len(data))
                    
                except:
                    time.sleep(120)
                    continue
    

        else:
            print(" Could Not find/create csv file to write to")



auth = tweepy.OAuthHandler(api_key,api_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(   auth, 
                    wait_on_rate_limit=True, 
                    wait_on_rate_limit_notify=True )

try:
    api.verify_credentials()
    print("twitter_KE_NLP Running")
    make_csv = CreateTweetsCsv(tweets_csv_file_name)
    make_csv.GetTweetsAndReplies(api, kword="sipangwingwi")

except tweepy.error.TweepError as error:
    print("Error : "+str(error))