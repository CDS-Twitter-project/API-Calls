import pprint
import argparse
import os.path
import json
from TwitterSearch import *

parser = argparse.ArgumentParser()
parser.add_argument("--out_file", help="the file to output results", default='data2.txt')
parser.add_argument("--include_entities", help="whether to include entitites", default=True)
parser.add_argument("--key_file", help="where to read in the keys from, which should be a file with four lines, containing the consumer_key, consumer_secret, access_token, and access_token secret (or just change the values in the script)")
parser.add_argument("--search_terms", help="search terms for the search", nargs='+', required=True)
parser.add_argument("--num_results", help="number of results you want", type=int, default=100)
parser.add_argument("--config_file", help="the config file with the tweet to start from", default="conf.txt")

args = parser.parse_args()
print "Search Terms: ", args.search_terms
keys = []  #a list containing the consumer key, consumer secret, access token, and access token secret
if args.key_file:
    with file(args.key_file) as key_file:
        for line in key_file:
            keys.append(line.strip())

else:
   keys.append('insert') #consumer key
   keys.append('your') #consumer secret
   keys.append('keys') #access token
   keys.append('here') #access token secret

tso = TwitterSearchOrder() # create a TwitterSearchOrder object
tso.set_keywords(args.search_terms) # let's define all words we would like to have a look for
tso.set_language('en') # english
tso.set_count(min(args.num_results, 100))
tso.set_include_entities(args.include_entities) # and give us all those entity information

iters = 1
if args.num_results > 100:
    args.num_results += 99
    iters = args.num_results / 100

print(tso.create_search_url());
start_point = 0
if os.path.isfile(args.config_file):
    with file(args.config_file) as fout:
        newest = fout.readlines()[-1]
        try:
            print 'Newest tweet already seen: %s' % newest
            if (int(newest) > 0):
                latest_seen = int(newest)
                tso.setSinceID(int(newest))
        except:
            print "No previous run"
else:
    print "No previous run"
# it's about time to create a TwitterSearch object with our secret tokens
ts = TwitterSearch(
    consumer_key = keys[0],
    consumer_secret = keys[1],
    access_token = keys[2],
    access_token_secret = keys[3]
 )
pp = pprint.PrettyPrinter(indent=4)

latest_id = 0
num_tweets = 0
next_max_id = 0
try:
    for i in range(iters):
        # first query the Twitter API
        response = ts.search_tweets(tso)

        # print rate limiting status
        print "Current api calls remaining: %s" % ts.get_metadata()['x-rate-limit-remaining']
        old_num_tweets = num_tweets
        # check all tweets according to their ID
        for tweet in response['content']['statuses']:
            num_tweets += 1
            tweet_id = tweet['id']

            with open(args.out_file,'a') as fout:
                json.dump(tweet, fout)
                fout.write('\n')
                #pprint.pprint(tweet,stream=fout)

            if (latest_id == 0):
                latest_id = tweet_id
            # current ID is lower than current next_max_id?
            if (tweet_id < next_max_id) or (next_max_id == 0):
                next_max_id = tweet_id
                next_max_id -= 1
        tso.set_max_id(next_max_id)
        if (num_tweets == old_num_tweets):
            #no tweets returned... i could also check if the length is equal to 0
            break

    print "Number of tweets seen: %i" % num_tweets
    if (num_tweets > 0):
        print "Oldest tweet id seen: %i" % next_max_id
        print "Newest tweet id seen: %i" % latest_id
        with open(args.config_file,'w') as fout:
            pprint.pprint(latest_id,stream=fout)
except:
    print "Newest tweet id seen: %i" % latest_id
    with open(args.config_file,'w') as fout:
        pprint.pprint(latest_id,stream=fout)
