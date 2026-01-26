# CloudFront Origin Access Identity for UI bucket
resource "aws_cloudfront_origin_access_identity" "ui_oai" {
  comment = "OAI for Spooky Days UI S3 bucket"
}

# S3 bucket policy to allow CloudFront OAI access
resource "aws_s3_bucket_policy" "ui_bucket_policy" {
  bucket = aws_s3_bucket.spooky_days_ui_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.ui_oai.iam_arn
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.spooky_days_ui_bucket.arn}/*"
      }
    ]
  })
}

# WAF Web ACL for DDoS protection
resource "aws_wafv2_web_acl" "cloudfront_waf" {
  name        = "${var.app_name}-cloudfront-waf"
  description = "WAF for CloudFront distribution"
  scope       = "CLOUDFRONT"

  default_action {
    allow {}
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.app_name}-cloudfront-waf"
    sampled_requests_enabled   = true
  }
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "spooky_days_distribution" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Spooky Days UI and API distribution"
  default_root_object = "index.html"

  # Custom domain
  aliases = local.domain_aliases

  # ACM certificate for HTTPS
  viewer_certificate {
    acm_certificate_arn = aws_acm_certificate.spooky_days_cert.arn
    ssl_support_method  = "sni-only"
  }

  depends_on = [
    aws_route53_record.spooky_days_cert_validation,
    aws_s3_bucket_ownership_controls.logs_bucket_ownership,
    aws_s3_bucket_public_access_block.logs_bucket_public_access_block,
    aws_s3_bucket_policy.logs_bucket_policy,
  ]

  # Origins
  origin {
    domain_name = aws_s3_bucket.spooky_days_ui_bucket.bucket_regional_domain_name
    origin_id   = "S3-UI"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.ui_oai.cloudfront_access_identity_path
    }
  }

  # Placeholder for API Gateway origin (to be added after apigateway.tf implementation)
  # origin {
  #   domain_name = "${aws_apigatewayv2_api.gallery_api.id}.execute-api.${var.aws_region}.amazonaws.com"
  #   origin_id   = "API-Gateway"
  #
  #   custom_origin_config {
  #     http_port              = 80
  #     https_port             = 443
  #     origin_protocol_policy = "https-only"
  #     origin_ssl_protocols   = ["TLSv1.2"]
  #   }
  # }

  # Default behavior (UI)
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-UI"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  # Disable caching for index.html to ensure latest version on refresh
  ordered_cache_behavior {
    path_pattern     = "/index.html"
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-UI"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
  }

  # Behavior for API routes (to be uncommented after API Gateway)
  # ordered_cache_behavior {
  #   path_pattern     = "/api/*"
  #   allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
  #   cached_methods   = ["GET", "HEAD"]
  #   target_origin_id = "API-Gateway"
  #
  #   forwarded_values {
  #     query_string = true
  #     cookies {
  #       forward = "all"
  #     }
  #     headers = ["Authorization"]
  #   }
  #
  #   viewer_protocol_policy = "redirect-to-https"
  #   min_ttl                = 0
  #   default_ttl            = 0
  #   max_ttl                = 0
  # }

  # Restrictions (whitelist US only)
  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US"]
    }
  }

  # WAF association
  web_acl_id = aws_wafv2_web_acl.cloudfront_waf.arn

  # Custom error pages (SPA fallback)
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  # Enable access logging
  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.spooky_days_logs_bucket.bucket_domain_name
    prefix          = "cloudfront/"
  }
}