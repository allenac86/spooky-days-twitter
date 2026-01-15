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

# Lambda bucket lifecycle variables
variable "s3_lambda_noncurrent_version_expiration_days" {
  description = "Number of days after which noncurrent object versions are deleted in lambda bucket"
  type        = number
  default     = 14
}

variable "s3_lambda_incomplete_multipart_upload_days" {
  description = "Number of days after which incomplete multipart uploads are aborted in lambda bucket"
  type        = number
  default     = 7
}

variable "s3_lambda_lifecycle_noncurrent_versions_enabled" {
  description = "Enable lifecycle rule for deleting noncurrent versions in lambda bucket"
  type        = bool
  default     = true
}

variable "s3_lambda_lifecycle_multipart_upload_cleanup_enabled" {
  description = "Enable lifecycle rule for aborting incomplete multipart uploads in lambda bucket"
  type        = bool
  default     = true
}

# Image bucket lifecycle variables
variable "s3_image_noncurrent_version_expiration_days" {
  description = "Number of days after which noncurrent object versions are deleted in image bucket"
  type        = number
  default     = 14
}

variable "s3_image_incomplete_multipart_upload_days" {
  description = "Number of days after which incomplete multipart uploads are aborted in image bucket"
  type        = number
  default     = 7
}

variable "s3_image_glacier_transition_days" {
  description = "Number of days after which objects are transitioned to Glacier Instant Retrieval in image bucket"
  type        = number
  default     = 30
}

variable "s3_image_lifecycle_noncurrent_versions_enabled" {
  description = "Enable lifecycle rule for deleting noncurrent versions in image bucket"
  type        = bool
  default     = true
}

variable "s3_image_lifecycle_multipart_upload_cleanup_enabled" {
  description = "Enable lifecycle rule for aborting incomplete multipart uploads in image bucket"
  type        = bool
  default     = true
}

variable "s3_image_lifecycle_glacier_transition_enabled" {
  description = "Enable lifecycle rule for transitioning objects to Glacier in image bucket"
  type        = bool
  default     = true
}

variable "s3_image_transition_storage_class" {
  description = "Storage class to transition objects to in image bucket"
  type        = string
  default     = "GLACIER_IR"
}