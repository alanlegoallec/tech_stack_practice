import boto3
import logging
import os
from functools import lru_cache
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

@lru_cache(maxsize=10)
def get_secret(secret_name, region_name="us-east-1"):
    """
    Securely fetch a plain string secret from AWS Secrets Manager.
    Expects the secret to be stored as a plain string, no JSON parsing.
    Uses LRU cache to avoid repeated Secrets Manager calls.
    """
    client = boto3.client("secretsmanager", region_name=region_name)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response.get("SecretString")
        if not secret_string:
            logger.error(f"Secret {secret_name} is empty or missing 'SecretString'")
            raise ValueError(f"Secret {secret_name} is empty or malformed")
        logger.info(f"✅ Successfully fetched secret: {secret_name}")
        return secret_string
    except ClientError as e:
        logger.error(f"❌ Failed to fetch secret {secret_name}: {e}")
        raise
