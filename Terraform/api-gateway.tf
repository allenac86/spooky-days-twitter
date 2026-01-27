resource "aws_apigatewayv2_api" "gallery_api" {
  name          = "${var.app_name}-gallery-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "gallery_lambda_integration" {
  api_id                 = aws_apigatewayv2_api.gallery_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.spooky_days_gallery_api_lambda_function.arn
  integration_method     = "POST"
  payload_format_version = "1.0" # ensure Lambda receives v1.0 event (has `path`)
}

resource "aws_apigatewayv2_route" "get_image_data" {
  api_id    = aws_apigatewayv2_api.gallery_api.id
  route_key = "GET /api/get-image-data"
  target    = "integrations/${aws_apigatewayv2_integration.gallery_lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "get_twitter_data" {
  api_id    = aws_apigatewayv2_api.gallery_api.id
  route_key = "GET /api/get-twitter-data"
  target    = "integrations/${aws_apigatewayv2_integration.gallery_lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.gallery_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "allow_apigateway_invoke_gallery" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.spooky_days_gallery_api_lambda_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_apigatewayv2_api.gallery_api.id}/*/*"
}
