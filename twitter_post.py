import boto3
import os
import re
import tweepy

bearer_token = r"%s" % os.environ['bearer_token']
api_key = os.environ['api_key']
api_secret = os.environ['api_secret']
access_token = os.environ['access_token']
access_token_secret = os.environ['access_token_secret']
dynamodb_table_name = os.environ['dynamodb_table_name']
jpg_bucket_name = os.environ['jpg_bucket_name']

twitter = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)

auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

s3_client = boto3.client('s3')
dynamodb = boto3.client('dynamodb')


def post_image_to_twitter(text_content, file_path):
    myMedia = r"%s" % file_path
    media = api.media_upload(filename=myMedia)
    media_id = media.media_id
    twitter.create_tweet(text=text_content, media_ids=[media_id])
    
    
def insert_space_before_capital(s):
    # Find all capital letters except the first and insert a space before them
    result = re.sub(r'(?<!^)(?=[A-Z])', ' ', s)
    return result


def put_item_in_table(table_nm, item):
    response = dynamodb.put_item(TableName=table_nm, Item=item)

    return response


def handler(event, context):
    os.chdir("/tmp")
    
    # only execute the labda function if the event is triggered by an S3 Object Upload
    if (event["Records"][0]["eventName"] == "ObjectCreated:Put"):
        key = event["Records"][0]["s3"]["object"]["key"]
        text = insert_space_before_capital(key.split("_")[-1].replace(".jpg", ""))
        caption = f"{text}"
        local_file_path = "/tmp/" + key
        print(text)
        print(local_file_path)

        # build dynamodb item for put_item_in_table function
        date_attribute = event["Records"][0]["eventTime"]
        fileName_attribute = key
        item = {'date': {'S': date_attribute},'fileName': {'S': fileName_attribute}}
        
        # download image from S3
        try:
            s3_client.download_file(jpg_bucket_name, key, local_file_path)
            print(f'File downlaoded to {local_file_path}')
        except Exception as e:
            print(e)
            return {
                "statusCode": 500,
                "body": "Error downloading file from S3"
            }

        # post image to Twitter
        try:
            post_image_to_twitter(caption, local_file_path)
            print(f'Tweet posted with caption: {caption}')
        except Exception as e:
            print(e)
            return {
                "statusCode": 500,
                "body": "Error posting tweet"
            }
        
        # add item to DynamoDB
        try:
            put_item_in_table(dynamodb_table_name, item)

            return {
                "statusCode": 200,
                "body": "Item added to DynamoDB successfully!"
            }
        except Exception as e:
            print(e)
            return {
                "statusCode": 500,
                "body": "Error adding item to DynamoDB"
            }
        
    else:
        return {
            "statusCode": 500,
            "body": "Event triggered by something other than an S3 Object Upload"
        }