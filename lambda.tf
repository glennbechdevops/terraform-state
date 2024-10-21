# Prefix variable
variable "prefix" {
  type        = string
  description = "Prefix for all resource names"
}

# IAM Role for Lambda Execution
resource "aws_iam_role" "lambda_exec_role" {
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        }
      }
    ]
  })

  name = "${var.prefix}_lambda_exec_role"
}

# Inline Policy for Amazon Comprehend with full access
resource "aws_iam_role_policy" "lambda_comprehend_policy" {
  name = "${var.prefix}_LambdaComprehendPolicy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "comprehend:*",
        "Resource": "*"
      }
    ]
  })
}

# Attach policy to the role
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda Function Resource
resource "aws_lambda_function" "comprehend_lambda" {
  function_name = "${var.prefix}_comprehend_lambda_function"
  runtime       = "python3.8"
  handler       = "comprehend.lambda_handler"
  role          = aws_iam_role.lambda_exec_role.arn
  filename      = "lambda_function_payload.zip"

  environment {
    variables = {
      LOG_LEVEL = "DEBUG"
    }
  }
}

# Lambda Function URL Resource
resource "aws_lambda_function_url" "comprehend_lambda_url" {
  function_name       = aws_lambda_function.comprehend_lambda.function_name
  authorization_type  = "NONE"
}

# Allow Lambda URL to invoke the function
resource "aws_lambda_permission" "allow_lambda_url" {
  statement_id          = "AllowLambdaURLInvoke"
  action                = "lambda:InvokeFunctionUrl"
  function_name         = aws_lambda_function.comprehend_lambda.function_name
  principal             = "*"
  function_url_auth_type = aws_lambda_function_url.comprehend_lambda_url.authorization_type
}

# Create a zip file from the Python code (using the local lambda_function.py)
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/comprehend.py"
  output_path = "${path.module}/lambda_function_payload.zip"
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "comprehend_log_group" {
  name              = "/aws/lambda/${var.prefix}_comprehend_lambda_function"
  retention_in_days = 7
}

output "lambda_url" {
  value =aws_lambda_function_url.comprehend_lambda_url.function_url
}
