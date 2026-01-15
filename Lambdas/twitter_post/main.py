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


def update_dynamodb_record(table_name, job_id, caption, status="posted"):
    try:
        # Query to get the existing record's timestamp
        query_response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression='job_id = :job_id',
            ExpressionAttributeValues={
                ':job_id': {'S': job_id}
            },
            Limit=1,
            ScanIndexForward=False
        )
        
        if not query_response.get('Items'):
            print(f"Error: No record found for job_id: {job_id}")
            raise ValueError(f"No record found for job_id: {job_id}")
        
        record_timestamp = query_response['Items'][0]['timestamp']['N']
        
        # Update the record with caption and status
        dynamodb.update_item(
            TableName=table_name,
            Key={
                'job_id': {'S': job_id},
                'timestamp': {'N': record_timestamp}
            },
            UpdateExpression='SET #status = :status, caption = :caption',
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':status': {'S': status},
                ':caption': {'S': caption}
            }
        )
        print(f"DynamoDB record updated for job_id: {job_id}")
    except dynamodb.exceptions.ResourceNotFoundException:
        print(f"Error: DynamoDB table not found")
        raise
    except dynamodb.exceptions.ConditionalCheckFailedException as e:
        print(f"Error: Conditional check failed: {e}")
        raise
    except ValueError as e:
        print(f"Error: {e}")
        raise
    except Exception as e:
        print(f"Error updating DynamoDB record: {e}")
        raise


def handler(event, context):
    os.chdir("/tmp")
    
    # only execute the labda function if the event is triggered by an S3 Object Upload
    if (event["Records"][0]["eventName"] == "ObjectCreated:Put"):
        key = event["Records"][0]["s3"]["object"]["key"]
        job_id = key.replace("images/", "")
        text = insert_space_before_capital(key.split("_")[-1].replace(".jpg", ""))
        caption = f"National {text} Day!"
        local_file_path = f"/tmp/{job_id}"
        print(f"Caption: {caption}")
        print(f"Local file path: {local_file_path}")
        print(f"Job ID: {job_id}")
        
        # download image from S3
        try:
            s3_client.download_file(image_bucket_name, key, local_file_path)
            print(f'File downloaded to {local_file_path}')
        except Exception as e:
            print(f"Error downloading file from S3: {e}")
            return {
                "statusCode": 500,
                "body": "Error downloading file from S3"
            }

        # post image to Twitter
        try:
            post_image_to_twitter(caption, local_file_path)
            print(f'Tweet posted with caption: {caption}')
        except Exception as e:
            print(f"Error posting tweet: {e}")
            return {
                "statusCode": 500,
                "body": "Error posting tweet"
            }
        
        # update DynamoDB record
        try:
            update_dynamodb_record(dynamodb_table_name, job_id, caption, "posted")
            return {
                "statusCode": 200,
                "body": "Tweet posted and DynamoDB record updated successfully!"
            }
        except Exception as e:
            print(f"Error updating DynamoDB record: {e}")
            return {
                "statusCode": 500,
                "body": "Error updating DynamoDB record"
            }
        
    else:
        return {
            "statusCode": 500,
            "body": "Event triggered by something other than an S3 Object Upload"
        }