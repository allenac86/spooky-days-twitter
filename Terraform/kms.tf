# KMS Key for encrypting Secrets Manager and S3
resource "aws_kms_key" "app_encryption_key" {
  description             = "KMS key for encrypting Secrets Manager secrets and S3 buckets"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow Lambda roles to use the key"
        Effect = "Allow"
        Principal = {
          AWS = [
            aws_iam_role.image_lambda_execution_role.arn,
            aws_iam_role.twitter_lambda_execution_role.arn
          ]
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow S3 to use the key"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_kms_alias" "app_encryption_key_alias" {
  name          = "alias/${var.app_name}-encryption-key"
  target_key_id = aws_kms_key.app_encryption_key.key_id
}
