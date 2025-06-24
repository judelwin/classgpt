import os
import boto3
from botocore.exceptions import ClientError

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_REGION = os.getenv("AWS_S3_REGION", "us-east-2")

s3_client = boto3.client(
    "s3",
    region_name=AWS_S3_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

def upload_file_to_s3(file_bytes, filename, user_id, class_id):
    """
    Uploads a file to S3 and returns the S3 URL.
    The file will be stored under user_id/class_id/filename for isolation.
    """
    key = f"{user_id}/{class_id}/{filename}"
    try:
        s3_client.put_object(Bucket=AWS_S3_BUCKET, Key=key, Body=file_bytes)
        url = f"https://{AWS_S3_BUCKET}.s3.{AWS_S3_REGION}.amazonaws.com/{key}"
        return url
    except ClientError as e:
        raise RuntimeError(f"Failed to upload to S3: {e}") 