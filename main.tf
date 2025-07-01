provider "aws" {
  region = "ap-south-1"
}

resource "aws_dynamodb_table" "trafficproj" {
  name           = "trafficproj"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "license"

  attribute {
    name = "license"
    type = "S"
  }
}

resource "aws_iam_user_policy_attachment" "dynamodb_full_access" {
  user       = "trafficproject"
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_user_policy_attachment" "rekognition_full_access" {
  user       = "trafficproject"
  policy_arn = "arn:aws:iam::aws:policy/AmazonRekognitionFullAccess"
}

resource "aws_iam_user_policy_attachment" "sns_full_access" {
  user       = "trafficproject"
  policy_arn = "arn:aws:iam::aws:policy/AmazonSNSFullAccess"
}