# spooky-days-twitter

[![Build](https://github.com/allenac86/spooky-days-twitter/actions/workflows/build.yml/badge.svg)](https://github.com/allenac86/spooky-days-twitter/actions/workflows/build.yml)
[![Deploy](https://github.com/allenac86/spooky-days-twitter/actions/workflows/deploy.yml/badge.svg)](https://github.com/allenac86/spooky-days-twitter/actions/workflows/deploy.yml)

A serverless Python application that generates images of various "National Days" with a spooky twist using OpenAI's DALL-E 3 and automatically posts them to Twitter (X) Monday through Friday at 8:00 AM EST.

**Status:** 🟢 Live and actively posting

I created this AWS serverless application while preparing for the AWS Developer Associate and Terraform Associate certifications to validate the knowledge and experience I've gained on the job.

## Architecture

**AWS Services Used:**
- **Lambda** - Serverless compute for image generation and Twitter posting
- **Lambda Layers** - Shared dependencies (OpenAI SDK, Tweepy, boto3)
- **S3** - Storage for Lambda code packages, generated images, and configuration
- **DynamoDB** - Job tracking and post history
- **EventBridge** - Cron-based scheduling (Mon-Fri at 1:00 PM UTC / 8:00 AM EST)
- **Secrets Manager** - Secure storage for OpenAI and Twitter API credentials
- **KMS** - Encryption for secrets at rest
- **CloudWatch Logs** - Lambda function logging and monitoring
- **IAM** - Role-based access control and permissions

**Application Flow:**

1. **EventBridge Cron Trigger** - Every weekday morning at 8:00 AM EST, EventBridge triggers the Image Generation Lambda
2. **Image Generation Lambda** - Retrieves the national-days.json configuration from S3, fetches OpenAI API credentials from Secrets Manager, generates spooky-themed images using DALL-E 3, uploads images to S3 (`images/` folder), and inserts job records into DynamoDB with status "uploaded"
3. **S3 Event Notification** - When an image is uploaded to S3, it automatically triggers the Twitter Post Lambda
4. **Twitter Post Lambda** - Downloads the image from S3, retrieves Twitter API credentials from Secrets Manager, posts the image to Twitter with a caption, and updates the DynamoDB record with the caption and status "posted"

**Infrastructure:**
- Managed via Terraform Cloud
- CI/CD via GitHub Actions (build → deploy pipeline)
- Lambda Layers built using official AWS Lambda Docker images for binary compatibility

Architecture Diagram (AI generated using Eraser [https://www.eraser.io/ai/aws-diagram-generator]):

<img width="4297" height="1745" alt="image" src="https://github.com/user-attachments/assets/b0748c4f-33da-49f5-8749-a92640fd22e1" />

Twitter Profile ([https://x.com/spooky_days_gpt]):
<img width="655" height="548" alt="image" src="https://github.com/user-attachments/assets/03a83fb0-a93e-4cb7-9ddd-ce7debb347c1" />

Example Twitter Post:
<img width="650" height="583" alt="image" src="https://github.com/user-attachments/assets/e9f94c35-df8e-404a-a65b-ad8fdf54c874" />

