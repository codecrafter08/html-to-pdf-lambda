import json
import os
import boto3
import pdfkit
from urllib.parse import urlparse
from dotenv import load_dotenv

WKHTMLTOPDF_PATH = "/usr/bin/wkhtmltopdf"
BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
load_dotenv()

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get("S3_AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("S3_AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("S3_AWS_REGION")
)


def convert_html_to_pdf(html_content, path_to_pdf, from_file=False):
    """
    Converts an HTML string to a PDF file in AWS Lambda.
    """
  
    options = {
        "page-size": "A2",  # Ensure A2 page size
        "margin-top": "10mm",
        "margin-bottom": "10mm",
        "margin-left": "10mm",
        "margin-right": "10mm",
        "encoding": "UTF-8",
        "enable-local-file-access": None,  # Required for local CSS
    }

    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    if from_file:
        pdfkit.from_file(html_content, path_to_pdf, options=options, configuration=config)
    else:
        pdfkit.from_string(html_content, path_to_pdf, options=options, configuration=config)

    print(f"PDF successfully created: {path_to_pdf}")
    return path_to_pdf  # Return the path for uploading


def handler(event, context):
    try:
        # Parse the request body
        body = json.loads(event.get("body", "{}"))
        html_body = body.get("html_body")
        upload_path = body.get("upload_path")
        path_to_pdf = body.get("path_to_pdf", "/tmp/result.pdf")
        s3_uri = body.get("s3_uri")
        from_file = False
        print("s3_uri",s3_uri)

        if s3_uri:
            parsed_uri = urlparse(s3_uri)
            object_key = parsed_uri.path.lstrip('/')
            file_name = os.path.basename(object_key)

            # Download HTML file from S3
            html_local_path = f"/tmp/{file_name}"
            pdf_local_path = html_local_path.replace(".html", ".pdf")
            pdf_s3_key = object_key.replace(".html", ".pdf")

            s3_client.download_file(BUCKET_NAME, object_key, html_local_path)
            print("File Downloaded Sucessfully")

            html_body = html_local_path
            path_to_pdf = pdf_local_path
            upload_path = pdf_s3_key
            from_file = True




        if html_body is None or upload_path is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'html_body' or 'upload_path' key in request."})
            }

        convert_html_to_pdf(html_body, path_to_pdf, from_file=from_file)
        s3_client.upload_file(path_to_pdf, BUCKET_NAME, upload_path, ExtraArgs={
            'ContentType': 'application/pdf',  # Ensure correct MIME type
            'ACL': 'public-read'  # Make the file publicly accessible
            })
        os.remove(path_to_pdf)

        # Construct the S3 URL. Note: This URL format assumes that the bucket is in the standard region.
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{upload_path}"

        return {
            "statusCode": 200,
            "body": json.dumps({"pdf_s3_url": s3_url})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }