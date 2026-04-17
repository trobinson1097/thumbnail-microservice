
# State file stored in S3, locking handled by DynamoDB

terraform {
  backend "s3" {
    bucket         = "your-state-bucket-name"  # update this 
    key            = "lambda/terraform.tfstate"
    region         = "us-east-2"
    dynamodb_table = "rock-of-ages-terraform-locks" 
    encrypt        = true
  }
}