import pprint
import argparse
from TwitterSearch import *

parser = argparse.ArgumentParser()
parser.add_argument("--since_id", help="since_id for query")
parser.add_argument("--out_file", help="the file to output results")
parser.add_argument("--include_entities", help="whether to include entitites")
parser.add_argument("--key_file", help="where to read in the keys")
args = parser.parse_args()


try:
    tso = TwitterSearchOrder() # create a TwitterSearchOrder object
    tso.setKeywords(['Coffee', 'NYC']) # let's define all words we would like to have a look for
    tso.setLanguage('en') # english
    tso.setCount(10) # 10 results per search call
    tso.setIncludeEntities(True) # and give us all those entity information

    # it's about time to create a TwitterSearch object with our secret tokens
    ts = TwitterSearch(
        consumer_key = 'insert',
        consumer_secret = 'your',
        access_token = 'keys',
        access_token_secret = 'here'
     )
    pp = pprint.PrettyPrinter(indent=4)

    response = ts.searchTweets(tso)

    todo = True
    latest_id = 0
    next_max_id = 0
    iters = 0

    while(todo):
        if (iters > 5):
            break

        # first query the Twitter API
        response = ts.searchTweets(tso)

        # print rate limiting status
        print "Current rate-limiting status: %s" % ts.getMetadata()['x-rate-limit-reset']

        # check if there are statuses returned and whether we still have work to do
        todo = not len(response['content']['statuses']) == 0

        # check all tweets according to their ID
        for tweet in response['content']['statuses']:
            tweet_id = tweet['id']

            print("Seen tweet with ID %i" % tweet_id)
            with open('data2.txt','a') as fout:
                pprint.pprint(tweet,stream=fout)

            if (latest_id == 0):
	        latest_id = tweet_id
            # current ID is lower than current next_max_id?
            if (tweet_id < next_max_id) or (next_max_id == 0):
                next_max_id = tweet_id
                next_max_id -= 1 # decrement to avoid seeing this tweet again

        # set lowest ID as MaxID
        tso.setMaxID(next_max_id)

        iters += 1
    next_max_id += 1
    print("Oldest tweet id seen: %i" % next_max_id)
    print("Newest tweet id seen: %i" % latest_id)

except TwitterSearchException as e: # take care of all those ugly errors if there are some
    print(e)