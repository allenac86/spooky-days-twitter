import boto3
import json
import os
import re
import tweepy

twitter_secret_arn = os.environ['TWITTER_SECRET_ARN']
dynamodb_table_name = os.environ['DYNAMODB_TABLE_NAME']
image_bucket_name = os.environ['IMAGE_BUCKET_NAME']

# Retrieve Twitter credentials from Secrets Manager
secrets_client = boto3.client('secretsmanager')
try:
    secret_response = secrets_client.get_secret_value(SecretId=twitter_secret_arn)
    twitter_credentials = json.loads(secret_response['SecretString'])
    access_token = twitter_credentials['ACCESS_TOKEN']
    access_token_secret = twitter_credentials['ACCESS_TOKEN_SECRET']
    api_key = twitter_credentials['API_KEY']
    api_secret = twitter_credentials['API_SECRET']
    bearer_token = twitter_credentials['BEARER_TOKEN']
except secrets_client.exceptions.ResourceNotFoundException:
    print("Error: Secret not found in Secrets Manager")
    raise
except secrets_client.exceptions.InvalidRequestException as e:
    print(f"Error: Invalid request to Secrets Manager: {e}")
    raise
except secrets_client.exceptions.InvalidParameterException as e:
    print(f"Error: Invalid parameter in Secrets Manager request: {e}")
    raise
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON in secret: {e}")
    raise
except KeyError as e:
    print(f"Error: Missing required credential in secret: {e}")
    raise
except Exception as e:
    print(f"Error retrieving secret from Secrets Manager: {e}")
    raise

twitter = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

dynamodb = boto3.client('dynamodb')
s3_client = boto3.client('s3')


def post_image_to_twitter(text_content, file_path):
    myMedia = r"%s" % file_path
    media = api.media_upload(filename=myMedia)
    media_id = media.media_id
    twitter.create_tweet(text=text_content, media_ids=[media_id])
    
    
def insert_space_before_capital(s):
    # Find all capital letters except the first and insert a space before them
    result = re.sub(r'(?<!^)(?=[A-Z])', ' ', s)
    return result

# TODO: implement correct dynamodb functionality
# def upload_to_dynamodb(table_nm, item):
#     response = dynamodb.put_item(TableName=table_nm, Item=item)

#     return response


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

        # build dynamodb item for upload_to_dynamodb function
        date_attribute = event["Records"][0]["eventTime"]
        fileName_attribute = key
        item = {'date': {'S': date_attribute},'fileName': {'S': fileName_attribute}}
        
        # download image from S3
        try:
            s3_client.download_file(image_bucket_name, key, local_file_path)
            print(f'File downloaded to {local_file_path}')
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
        # TODO implement correct dynamodb functionality
        # try:
        #     upload_to_dynamodb(dynamodb_table_name, item)

        #     return {
        #         "statusCode": 200,
        #         "body": "Item added to DynamoDB successfully!"
        #     }
        # except Exception as e:
        #     print(e)
        #     return {
        #         "statusCode": 500,
        #         "body": "Error adding item to DynamoDB"
        #     }
        
    else:
        return {
            "statusCode": 500,
            "body": "Event triggered by something other than an S3 Object Upload"
        }