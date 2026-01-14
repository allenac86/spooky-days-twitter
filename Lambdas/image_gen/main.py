from base64 import b64decode
import datetime
import json
import os

import boto3
import openai

bucket_name = os.environ['IMAGE_BUCKET_NAME']
dynamodb_table_name = os.environ['DYNAMODB_TABLE_NAME']

client = openai.OpenAI()
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

file = open('national-days.json')
national_days_json = json.load(file)
current_time = datetime.datetime.now()
day_of_month = str(current_time.day)
month_of_year = MONTH_DICT[str(current_time.month)]
file_prefix = month_of_year + "_" + day_of_month
b64_image_list = []

def generate_images(data, month, day, response_type, image_quality):
    for national_day in data[month][day]:
        response = client.images.generate(
            model="dall-e-3",
            prompt="National " + national_day + " Day, but with a nightmarish, horrifyingly evil twist. The image should be dark, evil, terrifying, and induce a sense of dread in the viewer. Do not adjust this prompt in any way.",
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

              
def upload_image_to_s3(filename, bucket):
    file_to_upload = filename.replace("/tmp/", "")
    s3_client.upload_file(filename, bucket, file_to_upload)


def handler(event, context):
    filename = ""

    try:
        generate_images(national_days_json, month_of_year, day_of_month, "b64_json", "hd")
        print("images generated, saving to temp filesystem")

        for indx, image_dict in enumerate(b64_image_list):
            filename = f'/tmp/{file_prefix}_{indx}_{image_dict["day"].replace(" ", "")}.jpg'
            
            with open(filename, 'wb') as f:
                f.write(b64decode(image_dict["image"]))
            
            print(f'{filename} saved to temp filesystem')

            print(f"Uploading image {filename} to S3")
            upload_image_to_s3(filename, bucket_name)
            print(f"Image {filename} uploaded to S3")

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

