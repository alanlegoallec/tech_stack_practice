import io
import logging
import uuid
from datetime import datetime
from functools import lru_cache

import boto3
import pandas as pd
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


def load_names_df():
    """Download the CSV from S3 and return as DataFrame."""
    bucket_name = "fullstack-practice-data"
    object_key = "uploads/names_and_numbers.csv"
    # Use default credential chain (IAM role in EC2)
    s3 = boto3.client("s3")

    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        body = response["Body"].read()
        df = pd.read_csv(io.BytesIO(body))
        return df
    except Exception as e:
        print(f"❌ Failed to load names from S3: {e}")
        return None


def log_multiplication_to_s3(
    user_input: float,
    multiplier: float,
    product: float,
    name: str,
    explanation: str,
    latency_ms: float,
    client_ip: str,
    bucket: str = "fullstack-practice-data",
    object_key: str = "outputs/multiplication_log.csv",
):
    s3 = boto3.client("s3")

    # Row to append
    new_row = {
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "user_input": user_input,
        "random_multiplier": multiplier,
        "product": product,
        "associated_name": name,
        "explanation": explanation,
        "inference_latency_ms": round(latency_ms, 2),
        "client_ip": client_ip,
    }

    # Try to get the existing file
    try:
        obj = s3.get_object(Bucket=bucket, Key=object_key)
        existing_df = pd.read_csv(io.BytesIO(obj["Body"].read()))
        df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)
    except s3.exceptions.NoSuchKey:
        df = pd.DataFrame([new_row])
    except Exception as e:
        print(f"⚠️ Failed to load existing log: {e}")
        df = pd.DataFrame([new_row])

    # Upload updated file
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    s3.put_object(Bucket=bucket, Key=object_key, Body=buffer.getvalue())
