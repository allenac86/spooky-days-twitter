import datetime
import json
import os
from base64 import b64decode

import boto3
import openai
from aws_lambda_powertools import Logger

logger = Logger(service='image_generation_lambda')

bucket_name = os.environ['IMAGE_BUCKET_NAME']
dynamodb_table_name = os.environ['DYNAMODB_TABLE_NAME']
openai_secret_arn = os.environ['OPENAI_SECRET_ARN']

# Retrieve OpenAI API key from Secrets Manager
secrets_client = boto3.client('secretsmanager')
try:
    secret_response = secrets_client.get_secret_value(SecretId=openai_secret_arn)
    openai_api_key = secret_response['SecretString']
except secrets_client.exceptions.ResourceNotFoundException:
    logger.error('Secret not found in Secrets Manager')
    raise
except secrets_client.exceptions.InvalidRequestException as e:
    logger.error('Invalid request to Secrets Manager', error=str(e))
    raise
except secrets_client.exceptions.InvalidParameterException as e:
    logger.error('Invalid parameter in Secrets Manager request', error=str(e))
    raise
except Exception as e:
    logger.error('Failed to retrieve secret from Secrets Manager', error=str(e))
    raise

client = openai.OpenAI(api_key=openai_api_key)
dynamodb_client = boto3.client('dynamodb')
s3_client = boto3.client('s3')

MONTH_DICT = {
    '1': 'january',
    '2': 'february',
    '3': 'march',
    '4': 'april',
    '5': 'may',
    '6': 'june',
    '7': 'july',
    '8': 'august',
    '9': 'september',
    '10': 'october',
    '11': 'november',
    '12': 'december',
}

try:
    response = s3_client.get_object(Bucket=bucket_name, Key='national-days.json')
    national_days_json = json.loads(response['Body'].read())
except s3_client.exceptions.NoSuchKey as e:
    logger.error('national-days.json not found in S3', bucket=bucket_name, error=str(e))
    raise
except json.JSONDecodeError as e:
    logger.error('Invalid JSON in national-days.json', error=str(e))
    raise
except Exception as e:
    logger.error(
        'Failed to read national-days.json from S3', bucket=bucket_name, error=str(e)
    )
    raise

current_time = datetime.datetime.now()
day_of_month = str(current_time.day)
month_of_year = MONTH_DICT[str(current_time.month)]
file_prefix = month_of_year + '_' + day_of_month
b64_image_list = []


def generate_images(data, month, day, response_type, image_quality):
    for national_day in data[month][day]:
        try:
            logger.info(
                'Generating image',
                national_day=national_day,
                model='dall-e-3',
                quality=image_quality,
            )
            response = client.images.generate(
                model='dall-e-3',
                prompt=national_days_json['Prompt'] + national_day + ' Day.',
                n=1,
                size='1024x1024',
                style='vivid',
                response_format=response_type,
                quality=image_quality,
            )

            b64_image_list.append(
                {
                    'created': datetime.datetime.now(),
                    'day': national_day,
                    'image': response.data[0].b64_json,
                }
            )
            logger.info('Image generated successfully', national_day=national_day)
        except Exception as e:
            logger.error(
                'Image generation failed', national_day=national_day, error=str(e)
            )
            raise


def upload_image_to_s3(filename, bucket):
    try:
        file_to_upload = filename.replace('/tmp/', '')
        s3_key = f'images/{file_to_upload}'
        s3_client.upload_file(filename, bucket, s3_key)
        logger.info('Image uploaded to S3', s3_key=s3_key)
    except Exception as e:
        logger.error('S3 upload failed', filename=filename, error=str(e))
        raise


def insert_dynamodb_record(job_id, status='pending'):
    try:
        timestamp = int(datetime.datetime.now().timestamp())
        dynamodb_client.put_item(
            TableName=dynamodb_table_name,
            Item={
                'job_id': {'S': job_id},
                'timestamp': {'N': str(timestamp)},
                'status': {'S': status},
            },
        )
        logger.info('DynamoDB record inserted', job_id=job_id, status=status)
    except Exception as e:
        logger.error('DynamoDB insert failed', job_id=job_id, error=str(e))
        raise


@logger.inject_lambda_context
def handler(event, context):
    filename = ''

    try:
        logger.info(
            'Starting image generation workflow', date=f'{month_of_year}_{day_of_month}'
        )
        generate_images(
            national_days_json, month_of_year, day_of_month, 'b64_json', 'hd'
        )

        for indx, image_dict in enumerate(b64_image_list):
            filename = (
                f'/tmp/{file_prefix}_{indx}_{image_dict["day"].replace(" ", "")}.jpg'
            )
            # the below line is for local testing,
            # comment it out when deploying to Lambda
            # filename = (
            #     f'{file_prefix}_{indx}_{image_dict["day"].replace(" ", "")}.jpg'
            # )

            with open(filename, 'wb') as f:
                f.write(b64decode(image_dict['image']))

            upload_image_to_s3(filename, bucket_name)
            insert_dynamodb_record(filename.replace('/tmp/', ''), 'uploaded')

        logger.info(
            'Image generation workflow completed', images_generated=len(b64_image_list)
        )
        return {
            'statusCode': 200,
            'body': json.dumps('Images generated and uploaded to S3'),
        }
    except Exception as e:
        logger.error('Image generation workflow failed', error=str(e))
        return {'statusCode': 500, 'body': json.dumps('Error generating images')}
