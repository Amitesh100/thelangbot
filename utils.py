# New function for getting the blacklist as a set of strings.
def getBlacklist(mycursor) -> set:
    mycursor.execute(
        "SELECT * FROM blacklist")
    myresult = mycursor.fetchall()
    # Convert list of tuples to set of strings
    usernames = set([row[0] for row in myresult])
    return usernames
   
        
# New function for getting the supporters as a set of strings.
def getSupporters(mycursor) -> set:
    mycursor.execute(
        "SELECT * FROM supporter")
    myresult = mycursor.fetchall()
    # Convert list of tuples to set of strings
    usernames = set([row[0] for row in myresult])
    return usernames
        

def retrieveLastSeenId(mycursor) -> int:
    mycursor.execute("SELECT * FROM tweet")
    myresult = mycursor.fetchall()
    return myresult[0][1]


def storeLastSeenId(mycursor, lastSeenId: int) -> None:
    exampleId: int = (lastSeenId)
    mycursor.execute("UPDATE tweet SET tweetId = '%s' WHERE id = 1", (exampleId,))
    mydb.commit()
    print(mycursor.rowcount, "record(s) affected", flush=True)
    return


def main(mycursor, myQuery: str) -> None:
    # Obtain last seen tweet
    lastSeenId: int = retrieveLastSeenId()
    print("Last seen tweet: " + str(lastSeenId) + "\n", flush=True)

    # Set up tweets from api
    # Only select tweets from our query and since our last seen tweet
    # Reverse the generator (which is an iterator, all generators are iterators, all iterators are iterables)
    # This makes the tweets ordered from oldest -> newest
    tweets = reversed(list(tweepy.Cursor(api.search, since_id=lastSeenId, q=myQuery).items()))

    # Setup current last seen tweet to be the previous one
    # This is just in case there are no items in the iterator
    currLastSeenId: int = lastSeenId

    # Setup tweeters frequency map for rate limit
    tweeters: dict[str, int] = {}

    # Get blacklist here
    blackList : set = getBlacklist()
        
    # Get supporters here
    supporters : set = getSupporters()
        
    for tweet in tweets:
        try:
            twitterUser: str = tweet.user.screen_name
            
            #Skip if user in blacklist
            if twitterUser in blackList:
                print("Blacklisted tweet by - @" + twitterUser, flush=True)
                continue
        
            # Add to frequency map
            if twitterUser not in tweeters:
                tweeters[twitterUser] = 1
            else:
                tweeters[twitterUser] += 1
        
            # Make sure they have not met rate limit of 2 tweets per 10 minutes
            if tweeters[twitterUser] <= 2:
                # Like tweet if supporter
                if twitterUser in supporters:
                    tweet.favorite()
                    print("Liking tweet by" + twitterUser, flush=True)

                # Retweet post
                print("Retweet Bot found tweet by @" + 
                    twitterUser + ". " + "Attempting to retweet...", flush=True)
                tweet.retweet()
                print(tweet.text, flush=True)
                print("Tweet retweeted!", flush=True)

            # Update last seen tweet with the newest tweet (bottom of list)
            currLastSeenId = tweet.id
            time.sleep(5)

        # Basic error handling - will print out why retweet failed to terminal
        except tweepy.TweepError as e:
            print(e.reason, "Tweet id: " + str(tweet.id), flush=True)
            if e.api_code == 185:
                print("Rate limit met, ending program", flush=True)
                break

        except StopIteration:
            print("Stopping...", flush=True)
            break
    
    # After iteration, store the last seen tweet id (newest)
    # Only store if it is different
    if(lastSeenId != currLastSeenId):
        storeLastSeenId(currLastSeenId)
        print("Updating last seen tweet to: " +
        str(currLastSeenId) + "\n", flush=True)

    return
