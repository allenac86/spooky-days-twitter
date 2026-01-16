# Secret for Image Gen Lambda
resource "aws_secretsmanager_secret" "image_gen_secrets" {
  name                    = "${var.app_name}-image-gen-secrets-${random_string.random.result}"
  description             = "Secrets for image generation lambda"
  kms_key_id              = aws_kms_key.app_encryption_key.id
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "image_gen_secrets" {
  secret_id     = aws_secretsmanager_secret.image_gen_secrets.id
  secret_string = var.openai_api_key
}

# Secret for Twitter Post Lambda
resource "aws_secretsmanager_secret" "twitter_secrets" {
  name                    = "${var.app_name}-twitter-secrets-${random_string.random.result}"
  description             = "Secrets for twitter post lambda"
  kms_key_id              = aws_kms_key.app_encryption_key.id
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "twitter_secrets" {
  secret_id = aws_secretsmanager_secret.twitter_secrets.id
  secret_string = jsonencode({
    ACCESS_TOKEN        = var.twitter_access_token
    ACCESS_TOKEN_SECRET = var.twitter_access_token_secret
    API_KEY             = var.twitter_api_key
    API_SECRET          = var.twitter_api_secret
    BEARER_TOKEN        = var.twitter_bearer_token
  })
}
