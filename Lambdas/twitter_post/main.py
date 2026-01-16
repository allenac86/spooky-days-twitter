import boto3
import json
import os
import re
import tweepy
from aws_lambda_powertools import Logger

logger = Logger(service="twitter_post")

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
    logger.error("Secret not found in Secrets Manager")
    raise
except secrets_client.exceptions.InvalidRequestException as e:
    logger.error("Invalid request to Secrets Manager", error=str(e))
    raise
except secrets_client.exceptions.InvalidParameterException as e:
    logger.error("Invalid parameter in Secrets Manager request", error=str(e))
    raise
except json.JSONDecodeError as e:
    logger.error("Invalid JSON in secret", error=str(e))
    raise
except KeyError as e:
    logger.error("Missing required credential in secret", error=str(e))
    raise
except Exception as e:
    logger.error("Failed to retrieve secret from Secrets Manager", error=str(e))
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
            logger.error("No record found for job_id", job_id=job_id)
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
        logger.info("DynamoDB record updated", job_id=job_id, status=status)
    except dynamodb.exceptions.ResourceNotFoundException:
        logger.error("DynamoDB table not found")
        raise
    except dynamodb.exceptions.ConditionalCheckFailedException as e:
        logger.error("Conditional check failed", error=str(e))
        raise
    except ValueError as e:
        logger.error("ValueError in DynamoDB update", error=str(e))
        raise
    except Exception as e:
        logger.error("DynamoDB update failed", job_id=job_id, error=str(e))
        raise


@logger.inject_lambda_context
def handler(event, context):
    os.chdir("/tmp")
    
    # only execute the labda function if the event is triggered by an S3 Object Upload
    if (event["Records"][0]["eventName"] == "ObjectCreated:Put"):
        key = event["Records"][0]["s3"]["object"]["key"]
        job_id = key.replace("images/", "")
        text = insert_space_before_capital(key.split("_")[-1].replace(".jpg", ""))
        caption = f"National {text} Day!"
        local_file_path = f"/tmp/{job_id}"
        logger.info("Processing S3 upload event", job_id=job_id, s3_key=key, caption=caption)
        
        # download image from S3
        try:
            s3_client.download_file(image_bucket_name, key, local_file_path)
            logger.info("Image downloaded from S3", s3_key=key, local_path=local_file_path)
        except Exception as e:
            logger.error("S3 download failed", s3_key=key, error=str(e))
            return {
                "statusCode": 500,
                "body": "Error downloading file from S3"
            }

        # post image to Twitter
        try:
            post_image_to_twitter(caption, local_file_path)
            logger.info("Tweet posted successfully", caption=caption, job_id=job_id)
        except Exception as e:
            logger.error("Twitter post failed", caption=caption, error=str(e))
            return {
                "statusCode": 500,
                "body": "Error posting tweet"
            }
        
        # update DynamoDB record
        try:
            update_dynamodb_record(dynamodb_table_name, job_id, caption, "posted")
            logger.info("Workflow completed successfully", job_id=job_id)
            return {
                "statusCode": 200,
                "body": "Tweet posted and DynamoDB record updated successfully!"
            }
        except Exception as e:
            logger.error("DynamoDB update failed in handler", job_id=job_id, error=str(e))
            return {
                "statusCode": 500,
                "body": "Error updating DynamoDB record"
            }
        
    else:
        logger.warning("Event not triggered by S3 ObjectCreated:Put", event_name=event["Records"][0]["eventName"])
        return {
            "statusCode": 500,
            "body": "Event triggered by something other than an S3 Object Upload"
        }