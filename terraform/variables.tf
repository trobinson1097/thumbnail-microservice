variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "image_bucket_name" {
  description = "Name of the S3 bucket containing images"
  type        = string
  default     = "your-image-bucket-name"
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "rock-of-ages-thumbnail-generator"
}