provider "aws" {
  region = "eu-west-1"
}

terraform {
  backend "s3" {
    bucket = "selva-terraform-state-bucket"
    region = "eu-west-1"
  }
}


resource "aws_s3_bucket" "buckets" {
  for_each = { for b in var.buckets : b.name => b }

  bucket = "${each.value.prefix}-${each.value.name}"
}

resource "aws_iam_role" "bucket_writer" {
  for_each = { for b in var.buckets : b.name => b }

  name = each.value.iam_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "bucket_write_policy" {
  for_each = { for b in var.buckets : b.name => b }

  name   = "${each.value.iam_role_name}-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["s3:PutObject"],
        Resource = "arn:aws:s3:::${aws_s3_bucket.buckets[each.key].id}/${each.value.write_prefix}*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_policy" {
  for_each = { for b in var.buckets : b.name => b }

  role       = aws_iam_role.bucket_writer[each.key].name
  policy_arn = aws_iam_policy.bucket_write_policy[each.key].arn
}
