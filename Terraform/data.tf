data "aws_caller_identity" "current" {}

data "aws_s3_object" "spooky_days_object" {
  bucket = aws_s3_bucket.spooky_days_lambda_bucket.bucket
  key    = var.image_lambda_zip_filename
}

data "aws_s3_object" "spooky_days_object_twitter" {
  bucket = aws_s3_bucket.spooky_days_lambda_bucket.bucket
  key    = var.twitter_lambda_zip_filename
}

data "aws_s3_object" "spooky_days_object_gallery" {
  bucket = aws_s3_bucket.spooky_days_lambda_bucket.bucket
  key    = var.gallery_lambda_zip_filename
}

data "aws_lambda_layer_version" "image_lambda_layer" {
  layer_name = var.image_lambda_layer_name
}

data "aws_lambda_layer_version" "twitter_lambda_layer" {
  layer_name = var.twitter_lambda_layer_name
}
