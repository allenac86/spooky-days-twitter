variable "app_name" {
  description = "Name of the application."
  type        = string
  default     = "spooky-days-gpt"
}

variable "cron_schedule" {
  description = "Cron schedule for Lambda function triggering."
  type        = string
  default     = "cron(0 13 ? * 2,3,4,5,6 *)"
}

variable "openai_api_key" {
  description = "OpenAI API key."
  type        = string
  sensitive   = true
}

variable "aws_region" {
  description = "AWS region."
  type        = string
  default     = "us-east-1"
}

variable "image_lambda_zip_filename" {
  description = "Filename of the Image Gen Lambda zip file."
  type        = string
  default     = null
}

variable "twitter_lambda_zip_filename" {
  description = "Filename of the Twitter Post Lambda zip file."
  type        = string
  default     = null
}

variable "image_lambda_layer_name" {
  description = "Name of the OpenAI Lambda layer."
  type        = string
  default     = null
}

variable "twitter_lambda_layer_name" {
  description = "Name of the Boto3 Lambda layer."
  type        = string
  default     = null
}

variable "image_bucket_name" {
  description = "Name of the S3 bucket for storing images."
  type        = string
  sensitive   = true
  default     = null
}

variable "twitter_bearer_token" {
  description = "Twitter bearer token."
  type        = string
  sensitive   = true
  default     = null
}

variable "twitter_api_key" {
  description = "Twitter API key."
  type        = string
  sensitive   = true
  default     = null
}

variable "twitter_api_secret" {
  description = "Twitter API secret."
  type        = string
  sensitive   = true
  default     = null
}

variable "twitter_access_token" {
  description = "Twitter access token."
  type        = string
  sensitive   = true
  default     = null
}

variable "twitter_access_token_secret" {
  description = "Twitter access token secret."
  type        = string
  sensitive   = true
  default     = null
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name"
  type        = string
  default     = null
}