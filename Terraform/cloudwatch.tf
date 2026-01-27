# CloudWatch Event Rule for scheduling
resource "aws_cloudwatch_event_rule" "lambda_schedule" {
  name                = local.cloudwatch_rule_name
  description         = "Cron job for Lambda"
  schedule_expression = var.cron_schedule
}

# CloudWatch Event Target to trigger the Image Gen Lambda
resource "aws_cloudwatch_event_target" "lambda" {
  rule = aws_cloudwatch_event_rule.lambda_schedule.name
  arn  = aws_lambda_function.spooky_days_image_lambda_function.arn
}

# CloudWatch Log Group for Image Lambda Function
resource "aws_cloudwatch_log_group" "image_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.spooky_days_image_lambda_function.function_name}"
  retention_in_days = 14
}

# CloudWatch Log Group for Twitter Lambda Function
resource "aws_cloudwatch_log_group" "twitter_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.spooky_days_twitter_lambda_function.function_name}"
  retention_in_days = 14
}

# CloudWatch Dashboard for Spooky Days Overview
resource "aws_cloudwatch_dashboard" "spooky_days_overview" {
  dashboard_name = "spooky-days-overview"

  dashboard_body = templatefile("${path.module}/dashboard-widgets.json", {
    dist_id        = aws_cloudfront_distribution.spooky_days_distribution.id,
    image_lambda   = aws_lambda_function.spooky_days_image_lambda_function.function_name,
    twitter_lambda = aws_lambda_function.spooky_days_twitter_lambda_function.function_name,
    gallery_lambda = aws_lambda_function.spooky_days_gallery_api_lambda_function.function_name,
    image_bucket   = aws_s3_bucket.spooky_days_image_bucket.bucket,
    metadata_table = aws_dynamodb_table.spooky_days_table.name,
    api_table      = aws_dynamodb_table.spooky_days_api_table.name
  })

  lifecycle {
    ignore_changes = [dashboard_body]
  }
}
