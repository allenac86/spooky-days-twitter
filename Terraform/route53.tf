# ACM Certificate for the spooky-days UI
resource "aws_acm_certificate" "spooky_days_cert" {
  domain_name               = var.hosted_zone
  subject_alternative_names = ["www.${var.hosted_zone}"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# Route 53 records for ACM certificate validation
resource "aws_route53_record" "spooky_days_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.spooky_days_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.spooky_days.zone_id
}

# Route 53 A record (alias) for each domain alias
resource "aws_route53_record" "domain_aliases" {
  for_each = toset(local.domain_aliases)

  zone_id = data.aws_route53_zone.spooky_days.zone_id
  name    = each.value
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.spooky_days_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.spooky_days_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}