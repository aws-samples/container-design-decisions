import boto3
import logging
import os
import json
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any, Union

bucket_name = os.getenv('S3_BUCKET_NAME', 'react-agent')

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def store_object(content: str, object_key: str) -> bool:
    try:
        # Create S3 client with optional region
        s3_client = boto3.client('s3')
        
        # Upload the string content directly
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=content
        )
        
        logger.info(f"Successfully stored content to s3://{bucket_name}/{object_key}")
        return True
        
    except ClientError as e:
        logger.error(f"Error storing content to S3: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error storing content to S3: {e}")
        return False
    
def load_object(object_key: str) -> Optional[str]:
    try:
        # Create S3 client with optional region
        s3_client = boto3.client('s3')
        
        # Get the object
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=object_key
        )
        
        # Read and return the content
        content = response['Body'].read().decode('utf-8')
        logger.info(f"Successfully loaded content from s3://{bucket_name}/{object_key}")
        return content
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            logger.warning(f"The object s3://{bucket_name}/{object_key} does not exist.")
        else:
            logger.error(f"Error loading content from S3: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading content from S3: {e}")
        return None    