# KMS Key for encrypting Secrets Manager and S3
resource "aws_kms_key" "secrets_manager_key" {
  description             = "KMS key for encrypting Secrets Manager secrets and S3 buckets"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_kms_alias" "secrets_manager_key_alias" {
  name          = "alias/${var.app_name}-secrets-key"
  target_key_id = aws_kms_key.secrets_manager_key.key_id
}
