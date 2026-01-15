locals {
  cloudwatch_rule_name               = "${var.app_name}-lambda-schedule-rule-${random_string.random.result}"
  image_lambda_execution_role_name   = "${var.app_name}-image-gen-lambda-execution-role-${random_string.random.result}"
  image_lambda_function_name         = "${var.app_name}-image-lambda-function-${random_string.random.result}"
  twitter_lambda_execution_role_name = "${var.app_name}-twitter-lambda-execution-role-${random_string.random.result}"
  twitter_lambda_function_name       = "${var.app_name}-twitter-lambda-function-${random_string.random.result}"
}

# Random String for S3 Bucket Name
resource "random_string" "random" {
  length  = 7
  lower   = true
  special = false
  upper   = false
}

# IAM Role for Image Lambda Execution
resource "aws_iam_role" "image_lambda_execution_role" {
  name = local.image_lambda_execution_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect = "Allow"
        Sid    = ""
      }
    ]
  })
}

# IAM Role for Twitter Lambda Execution
resource "aws_iam_role" "twitter_lambda_execution_role" {
  name = local.twitter_lambda_execution_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect = "Allow"
        Sid    = ""
      }
    ]
  })
}

# Grant the Image Lambda function permission to upload files to the image bucket
resource "aws_iam_policy" "spooky_days_image_bucket_policy" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = "${aws_s3_bucket.spooky_days_image_bucket.arn}/*"
      }
    ]
  })
}

# Grant the Twitter Lambda function permission to read s3 bucket events for execution
resource "aws_iam_policy" "spooky_days_twitter_bucket_policy" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.spooky_days_image_bucket.arn}",
          "${aws_s3_bucket.spooky_days_image_bucket.arn}/*"
        ]
      }
    ]
  })
}

# Grant the Image Lambda function permission to access DynamoDB
resource "aws_iam_policy" "spooky_days_image_dynamodb_policy" {
  name = "${var.app_name}-image-lambda-dynamodb-policy-${random_string.random.result}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.spooky_days_table.arn,
          "${aws_dynamodb_table.spooky_days_table.arn}/index/*"
        ]
      }
    ]
  })
}

# Grant the Twitter Lambda function permission to access DynamoDB
resource "aws_iam_policy" "spooky_days_twitter_dynamodb_policy" {
  name = "${var.app_name}-twitter-lambda-dynamodb-policy-${random_string.random.result}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.spooky_days_table.arn,
          "${aws_dynamodb_table.spooky_days_table.arn}/index/*"
        ]
      }
    ]
  })
}

# Grant Image Lambda permission to access secrets
resource "aws_iam_policy" "image_lambda_secrets_policy" {
  name        = "${var.app_name}-image-lambda-secrets-policy-${random_string.random.result}"
  description = "Policy for Image Lambda to access secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = aws_secretsmanager_secret.image_gen_secrets.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = aws_kms_key.secrets_manager_key.arn
      }
    ]
  })
}

# Grant Twitter Lambda permission to access secrets
resource "aws_iam_policy" "twitter_lambda_secrets_policy" {
  name        = "${var.app_name}-twitter-lambda-secrets-policy-${random_string.random.result}"
  description = "Policy for Twitter Lambda to access secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = aws_secretsmanager_secret.twitter_secrets.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = aws_kms_key.secrets_manager_key.arn
      }
    ]
  })
}

# IAM Policy to Allow Lambda Functions to Write Logs
resource "aws_iam_policy" "lambda_logging_policy" {
  name = "lambda_logging_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_policy_attachment" {
  role       = aws_iam_role.image_lambda_execution_role.name
  policy_arn = aws_iam_policy.spooky_days_image_bucket_policy.arn
}

resource "aws_iam_role_policy_attachment" "image_lambda_dynamodb_attachment" {
  role       = aws_iam_role.image_lambda_execution_role.name
  policy_arn = aws_iam_policy.spooky_days_image_dynamodb_policy.arn
}

resource "aws_iam_role_policy_attachment" "image_lambda_secrets_attachment" {
  role       = aws_iam_role.image_lambda_execution_role.name
  policy_arn = aws_iam_policy.image_lambda_secrets_policy.arn
}

resource "aws_iam_role_policy_attachment" "image_lambda_logging_attachment" {
  role       = aws_iam_role.image_lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_logging_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_s3_read_policy_attachment" {
  role       = aws_iam_role.twitter_lambda_execution_role.name
  policy_arn = aws_iam_policy.spooky_days_twitter_bucket_policy.arn
}

resource "aws_iam_role_policy_attachment" "twitter_lambda_dynamodb_attachment" {
  role       = aws_iam_role.twitter_lambda_execution_role.name
  policy_arn = aws_iam_policy.spooky_days_twitter_dynamodb_policy.arn
}

resource "aws_iam_role_policy_attachment" "twitter_lambda_secrets_attachment" {
  role       = aws_iam_role.twitter_lambda_execution_role.name
  policy_arn = aws_iam_policy.twitter_lambda_secrets_policy.arn
}

resource "aws_iam_role_policy_attachment" "twitter_lambda_logging_attachment" {
  role       = aws_iam_role.twitter_lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_logging_policy.arn
}

# Grant the Image Gen Lambda function permission to access the S3 bucket
resource "aws_lambda_permission" "allow_image_lambda_bucket_access" {
  statement_id  = "AllowExecutionFromLambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.spooky_days_image_lambda_function.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.spooky_days_lambda_bucket.arn
}

# Permission for CloudWatch to trigger the Image Gen Lambda
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.spooky_days_image_lambda_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_schedule.arn
}

resource "aws_lambda_permission" "allow_twitter_lambda_s3_execution" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.spooky_days_twitter_lambda_function.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.spooky_days_image_bucket.arn
}

# S3 bucket notification configuration
resource "aws_s3_bucket_notification" "image_bucket_notification" {
  bucket = aws_s3_bucket.spooky_days_image_bucket.bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.spooky_days_twitter_lambda_function.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".jpg"
  }

  depends_on = [aws_lambda_permission.allow_twitter_lambda_s3_execution]
}

