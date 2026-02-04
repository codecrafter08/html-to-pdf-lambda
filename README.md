# Docker Lambda HTML to PDF Converter

This project is a containerized AWS Lambda function that converts HTML content to PDF documents using `wkhtmltopdf` and `pdfkit`, and uploads the generated PDF to an Amazon S3 bucket.

## Features

- **HTML to PDF Conversion**: Converts raw HTML strings or HTML files stored in S3 to PDF.
- **S3 Integration**: Downloads source HTML from S3 and uploads the generated PDF back to S3.
- **Dockerized**: Packaged as a Docker container for easy deployment to AWS Lambda.
- **Customizable**: Supports custom page sizes (A2), margins, and encoding.

## Prerequisites

- Docker
- AWS CLI configured with appropriate permissions
- Python 3.x

## Project Structure

- `lambda_function.py`: The main Lambda handler and conversion logic.
- `Dockerfile`: Configuration for building the Docker image.
- `requirements.txt`: Python dependencies.
- `.env`: Environment variables (excluded from git).
- `.env.sample`: Template for environment variables.

## Configuration

1.  Copy the sample environment file:
    ```bash
    cp .env.sample .env
    ```

2.  Update `.env` with your AWS credentials and configuration:
    - `S3_AWS_ACCESS_KEY_ID`: Your AWS Access Key ID
    - `S3_AWS_SECRET_ACCESS_KEY`: Your AWS Secret Access Key
    - `S3_AWS_REGION`: AWS Region (e.g., us-west-1)
    - `S3_BUCKET_NAME`: Your S3 Bucket Name
    - `LD_LIBRARY_PATH`: Path to libraries (default: `/opt/lib`)
    - `FONTCONFIG_PATH`: Path to fonts (default: `/opt/fonts`)

## Usage

The Lambda function accepts a JSON payload with the following parameters:

### Request Body Parameters

- `html_body` (string): The raw HTML content to convert (optional if `s3_uri` is provided).
- `upload_path` (string): The destination path in the S3 bucket for the generated PDF.
- `s3_uri` (string): The S3 URI of an HTML file to convert (e.g., `s3://bucket-name/path/to/file.html`). If provided, `html_body` is ignored.
- `path_to_pdf` (string): Temporary local path for the PDF file (default: `/tmp/result.pdf`).

### Example Payloads

**Convert Raw HTML:**
```json
{
  "html_body": "<h1>Hello World</h1>",
  "upload_path": "pdfs/hello.pdf"
}
```

**Convert from S3 File:**
```json
{
  "s3_uri": "s3://my-bucket/templates/invoice.html",
  "upload_path": "invoices/invoice_123.pdf"
}
```

### Response

On success, returns a JSON object with the S3 URL of the generated PDF:

```json
{
  "statusCode": 200,
  "body": "{\"pdf_s3_url\": \"https://bellemar.s3.amazonaws.com/pdfs/hello.pdf\"}"
}
```

## Deployment

To build and push the Docker image to AWS ECR, use the following commands:

```sh
# Login to AWS ECR
aws ecr get-login-password --region us-west-1 --profile <your-profile> | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-west-1.amazonaws.com

# Build the image (multi-platform support)
docker buildx build --platform linux/amd64 -t htmltopdf-lambda:<tag> .

# Tag the image for ECR
docker image tag htmltopdf-lambda:<tag> <your-account-id>.dkr.ecr.<region>.amazonaws.com/htmltopdf-lambda:<tag>

# Push the image to ECR
docker image push <your-account-id>.dkr.ecr.<region>.amazonaws.com/htmltopdf-lambda:<tag>
```

Replace `<your-profile>`, `<your-account-id>`, `<region>`, and `<tag>` with your specific values.

## License

[Add License Information Here]
