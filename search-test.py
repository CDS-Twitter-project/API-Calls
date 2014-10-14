import pprint
import argparse
import os.path
from TwitterSearch import *

parser = argparse.ArgumentParser()
parser.add_argument("--out_file", help="the file to output results", default='data2.txt')
parser.add_argument("--include_entities", help="whether to include entitites", default=True)
parser.add_argument("--key_file", help="where to read in the keys from, which should be a file with four lines, containing the consumer_key, consumer_secret, access_token, and access_token secret (or just change the values in the script)")
parser.add_argument("--search_terms", help="search terms for the search", nargs='+', required=True)
parser.add_argument("--num_results", help="number of results you want", default=100)

args = parser.parse_args()
print "Search Terms: ", args.search_terms
keys = []  #a list containing the consumer key, consumer secret, access token, and access token secret
if args.out_file:
    with file(args.key_file) as key_file:
        for line in key_file:
            keys.append(line.strip())

else:
   keys.append('insert') #consumer key
   keys.append('your') #consumer secret
   keys.append('keys') #access token
   keys.append('here') #access token secret

tso = TwitterSearchOrder() # create a TwitterSearchOrder object
tso.setKeywords(args.search_terms) # let's define all words we would like to have a look for
tso.setLanguage('en') # english
tso.setCount(args.num_results)
tso.setIncludeEntities(args.include_entities) # and give us all those entity information

start_point = 0
if os.path.isfile(args.out_file):
    with file(args.out_file) as fout:
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

response = ts.searchTweets(tso)

latest_id = 0
num_tweets = 0
next_max_id = 0

# first query the Twitter API
response = ts.searchTweets(tso)

# print rate limiting status
print "Current api calls remaining: %s" % ts.getMetadata()['x-rate-limit-remaining']

# check all tweets according to their ID
for tweet in response['content']['statuses']:
    num_tweets += 1
    tweet_id = tweet['id']

    print("Seen tweet with ID %i" % tweet_id)
    with open(args.out_file,'a') as fout:
        pprint.pprint(tweet,stream=fout)

    if (latest_id == 0):
        latest_id = tweet_id
    # current ID is lower than current next_max_id?
    if (tweet_id < next_max_id) or (next_max_id == 0):
        next_max_id = tweet_id


print "Number of tweets seen: %i" % num_tweets
if (num_tweets > 0):
    print "Oldest tweet id seen: %i" % next_max_id
    print "Newest tweet id seen: %i" % latest_id
    with open(args.out_file,'a') as fout:
        pprint.pprint(latest_id,stream=fout)


