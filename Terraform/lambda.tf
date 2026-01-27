# Image Gen Lambda Function
resource "aws_lambda_function" "spooky_days_image_lambda_function" {
  function_name    = local.image_lambda_function_name
  role             = aws_iam_role.image_lambda_execution_role.arn
  handler          = "main.handler"
  s3_bucket        = aws_s3_bucket.spooky_days_lambda_bucket.bucket
  s3_key           = data.aws_s3_object.spooky_days_object.key
  source_code_hash = data.aws_s3_object.spooky_days_object.etag

  runtime = "python3.10"

  timeout = 120

  layers = [
    data.aws_lambda_layer_version.image_lambda_layer.arn,
  ]

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_image_table_name
      IMAGE_BUCKET_NAME   = var.image_bucket_name
      OPENAI_SECRET_ARN   = aws_secretsmanager_secret.image_gen_secrets.arn
    }
  }
}

# Twitter Post Lambda Function
resource "aws_lambda_function" "spooky_days_twitter_lambda_function" {
  function_name    = local.twitter_lambda_function_name
  role             = aws_iam_role.twitter_lambda_execution_role.arn
  handler          = "main.handler"
  s3_bucket        = aws_s3_bucket.spooky_days_lambda_bucket.bucket
  s3_key           = data.aws_s3_object.spooky_days_object_twitter.key
  source_code_hash = data.aws_s3_object.spooky_days_object_twitter.etag

  runtime = "python3.10"

  timeout = 120

  layers = [
    data.aws_lambda_layer_version.twitter_lambda_layer.arn,
  ]

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_image_table_name
      IMAGE_BUCKET_NAME   = var.image_bucket_name
      TWITTER_SECRET_ARN  = aws_secretsmanager_secret.twitter_secrets.arn
    }
  }
}

# Gallery API Lambda Function
resource "aws_lambda_function" "spooky_days_gallery_api_lambda_function" {
  function_name    = local.gallery_lambda_function_name
  role             = aws_iam_role.gallery_lambda_execution_role.arn
  handler          = "dist/src/handler.handler"
  s3_bucket        = aws_s3_bucket.spooky_days_lambda_bucket.bucket
  s3_key           = data.aws_s3_object.spooky_days_object_gallery.key
  source_code_hash = data.aws_s3_object.spooky_days_object_gallery.etag

  runtime = "nodejs22.x"

  timeout = 120

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_api_table_name
      IMAGE_BUCKET_NAME   = var.image_bucket_name
      ORIGIN_HEADER_NAME  = var.cloudfront_api_header_name
      ORIGIN_HEADER_VALUE = var.cloudfront_api_header_value
      TWITTER_SECRET_ARN  = aws_secretsmanager_secret.twitter_secrets.arn
    }
  }
}