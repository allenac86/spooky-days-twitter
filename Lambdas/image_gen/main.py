from base64 import b64decode
import datetime
import json
import os

import boto3
import openai

bucket_name = os.environ['IMAGE_BUCKET_NAME']
dynamodb_table_name = os.environ['DYNAMODB_TABLE_NAME']
openai_secret_arn = os.environ['OPENAI_SECRET_ARN']

# Retrieve OpenAI API key from Secrets Manager
secrets_client = boto3.client('secretsmanager')
try:
    secret_response = secrets_client.get_secret_value(SecretId=openai_secret_arn)
    openai_api_key = secret_response['SecretString']
except secrets_client.exceptions.ResourceNotFoundException:
    print("Error: Secret not found in Secrets Manager")
    raise
except secrets_client.exceptions.InvalidRequestException as e:
    print(f"Error: Invalid request to Secrets Manager: {e}")
    raise
except secrets_client.exceptions.InvalidParameterException as e:
    print(f"Error: Invalid parameter in Secrets Manager request: {e}")
    raise
except Exception as e:
    print(f"Error retrieving secret from Secrets Manager: {e}")
    raise

client = openai.OpenAI(api_key=openai_api_key)
dynamodb_client = boto3.client('dynamodb')
s3_client = boto3.client('s3')

MONTH_DICT = {
    "1": "january",
    "2": "february",
    "3": "march",
    "4": "april",
    "5": "may",
    "6": "june",
    "7": "july",
    "8": "august",
    "9": "september",
    "10": "october",
    "11": "november",
    "12": "december"
}

try:
    response = s3_client.get_object(Bucket=bucket_name, Key='national-days.json')
    national_days_json = json.loads(response['Body'].read())
except s3_client.exceptions.NoSuchKey as e:
    print(f"Error: national-days.json not found in S3 bucket: {e}")
    raise
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON in national-days.json: {e}")
    raise
except Exception as e:
    print(f"Error reading national-days.json from S3: {e}")
    raise

current_time = datetime.datetime.now()
day_of_month = str(current_time.day)
month_of_year = MONTH_DICT[str(current_time.month)]
file_prefix = month_of_year + "_" + day_of_month
b64_image_list = []

def generate_images(data, month, day, response_type, image_quality):
    for national_day in data[month][day]:
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=national_days_json["Prompt"] + national_day + " Day.",
                n=1,
                size="1024x1024",
                style="vivid",
                response_format=response_type,
                quality=image_quality
            )

            b64_image_list.append({
                "created": datetime.datetime.now(),
                "day": national_day,
                "image": response.data[0].b64_json
            })
        except Exception as e:
            print(f"Error generating image for {national_day}: {e}")
            raise

              
def upload_image_to_s3(filename, bucket):
    try:
        file_to_upload = filename.replace("/tmp/", "")
        s3_key = f"images/{file_to_upload}"
        s3_client.upload_file(filename, bucket, s3_key)
    except Exception as e:
        print(f"Error uploading {filename} to S3: {e}")
        raise


def insert_dynamodb_record(job_id, status="pending"):
    try:
        timestamp = int(datetime.datetime.now().timestamp())
        dynamodb_client.put_item(
            TableName=dynamodb_table_name,
            Item={
                'job_id': {'S': job_id},
                'timestamp': {'N': str(timestamp)},
                'status': {'S': status}
            }
        )
    except Exception as e:
        print(f"Error inserting DynamoDB record for {job_id}: {e}")
        raise


def handler(event, context):
    filename = ""

    try:
        generate_images(national_days_json, month_of_year, day_of_month, "b64_json", "hd")
        print("images generated, saving to temp filesystem")

        for indx, image_dict in enumerate(b64_image_list):
            filename = f'/tmp/{file_prefix}_{indx}_{image_dict["day"].replace(" ", "")}.jpg'
            # the below line is for local testing, comment it out when deploying to Lambda
            # filename = f'{file_prefix}_{indx}_{image_dict["day"].replace(" ", "")}.jpg'
            
            with open(filename, 'wb') as f:
                f.write(b64decode(image_dict["image"]))
            
            print(f'{filename} saved to temp filesystem')
            print(f"Uploading image {filename} to S3")

            upload_image_to_s3(filename, bucket_name)

            print(f"Image {filename} uploaded to S3")
            print(f"Inserting DynamoDB record for {filename}")

            insert_dynamodb_record(filename.replace("/tmp/", ""), "uploaded")

            print(f"DynamoDB record inserted for {filename}")

        return {
            "statusCode": 200,
            "body": json.dumps("Images generated and uploaded to S3")
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "body": json.dumps("Error generating images")
        }
