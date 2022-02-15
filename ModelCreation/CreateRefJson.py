import json
import string
import json
import pandas as pd

'''
This file creates the initial JSON
containing the lookup dictionary for convering 
the characters to numbers
'''
path_to_json_converter = "ref_converter.json"

ref_init_dict = dict()

numbers = [i for i in range(10)]

# Incase you need to transform back the models output,
# you might not always know what should have been uppercase
# and what was small if i have all letters as lowercase initially.
# It's just safer to have both in the dict
# >>> "A"=="a"  : False

l_letters = [l for l in string.ascii_lowercase]
u_letters = [l for l in string.ascii_uppercase]
punctuations  = [p for p in string.punctuation]

# Have items that occur more frequently at the beginning
# e.g lowercase letters
all_items = l_letters + u_letters + punctuations + numbers

ref_init_dict[None] = 0 # Allow for filling to fit length

for ind, item in enumerate(all_items):
    # +1 to allow as to use zero to fill in lengths
    ref_init_dict[item] = ind+1

with open(path_to_json_converter,'w') as f:
    json.dump(ref_init_dict,f,indent=4)


# Adding more characters to the JSON using collected tweets
with open(path_to_json_converter) as ref_json:
    ref_dict= json.load(ref_json)

data = pd.read_csv("Tweets.csv",index_col=[0])
data = data.dropna()

def convert_to_numb(s):
    global ref_dict
    # Remove leading and trailing gaps and return all character/letters
    l = list(s.strip())

    result = list(map(ref_dict.get,l))
    
    if None in result:
        with open(path_to_json_converter,'r+') as file:
            dict_data = json.load(file)
            value = max(dict_data.values())

            for item in l:
                if item not in dict_data:
                    value += 1
                    dict_data[item] = value

            file.seek(0)
            ref_dict = dict_data
            json.dump(ref_dict, file,indent=4)
        
            result = list(map(ref_dict.get,l))
        
    result  = result + [0]*(140 - len(result))

    return result


# Return the tweet and reply columns with the converted text
tweet_col = data["Reply"].apply(convert_to_numb )
reply_col = data["Reply"].apply(convert_to_numb)