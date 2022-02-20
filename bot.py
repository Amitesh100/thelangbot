import os, mysql.connector, time, tweepy
from utils import *

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

""" 
Dev NOTE: For testing purposes set the items(limit=3) to only get three tweets and test.
Also the logs will have the most recent tweet ID if needed / can check Twitter web.
"""

# Setup OAuth authentication for Tweepy
auth = tweepy.OAuthHandler(os.getenv("API_KEY"), os.getenv("API_SECRET_KEY"))
auth.set_access_token(os.getenv("ACCESS_TOKEN"), os.getenv("ACCESS_SECRET"))
# Rate limit = True: allows us to wait 15 minutes before retrying request
api = tweepy.API(auth, wait_on_rate_limit=True)

# Setup MySQL db
mydb = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_DB"))
mycursor = mydb.cursor()


if __name__ == "__main__":
    main("#langtwt OR #100DaysOfLanguage OR 100daysoflanguage -filter:retweets -result_type:recent")
    mycursor.close()
    mydb.close()
    print("\nRetweet function completed and db connection closed", flush=True)
