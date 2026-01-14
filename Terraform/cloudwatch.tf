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
