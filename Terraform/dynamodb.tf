resource "aws_dynamodb_table" "spooky_days_table" {
  name         = var.dynamodb_image_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "job_id"
  range_key    = "timestamp"

  attribute {
    name = "job_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  attribute {
    name = "status"
    type = "S"
  }

  global_secondary_index {
    name            = "status-timestamp-index"
    hash_key        = "status"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }
}

resource "aws_dynamodb_table" "spooky_days_api_table" {
  name         = var.dynamodb_api_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "query_id"
  range_key    = "timestamp"

  attribute {
    name = "query_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  attribute {
    name = "user"
    type = "S"
  }

  attribute {
    name = "path"
    type = "S"
  }

  global_secondary_index {
    name            = "user-path-index"
    hash_key        = "user"
    range_key       = "path"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }
}
