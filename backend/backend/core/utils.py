import io
import json
import logging
import os
import uuid
from datetime import datetime
from functools import lru_cache

import boto3
import pandas as pd
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# --- Constants ---
S3_BUCKET = "fullstack-practice-data"
NAMES_CSV_KEY = "uploads/names_and_numbers.csv"
LOG_CSV_KEY = "outputs/multiplication_log.csv"
DEFAULT_REGION = "us-east-1"


def require_env_var(key: str) -> str:
    """Fetch a required environment variable, or raise clear error if missing."""
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    else:
        logger.debug(f"✅ Loaded env var {key}")
    return value


@lru_cache(maxsize=10)
def get_secret_value(secret_name: str, region_name: str = "us-east-1") -> str:
    client = boto3.client("secretsmanager", region_name=region_name)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response.get("SecretString")
        if not secret_string:
            raise ValueError(f"Secret {secret_name} is empty or malformed")
        secret_dict = json.loads(secret_string)
        if len(secret_dict) != 1:
            raise ValueError(f"Secret {secret_name} should contain exactly one key")
        value = next(iter(secret_dict.values()))
        return value
    except (ClientError, ValueError) as e:
        logger.error(f"❌ Failed to fetch secret '{secret_name}': {e}")
        raise


def load_names_df(
    bucket: str = S3_BUCKET, object_key: str = NAMES_CSV_KEY
) -> pd.DataFrame | None:
    """Download the names CSV from S3 and return it as a DataFrame."""
    s3 = boto3.client("s3")
    try:
        response = s3.get_object(Bucket=bucket, Key=object_key)
        body = response["Body"].read()
        df = pd.read_csv(io.BytesIO(body))
        logger.info(f"✅ Loaded names CSV from s3://{bucket}/{object_key}")
        return df
    except Exception as e:
        logger.warning(f"❌ Failed to load names from s3://{bucket}/{object_key}: {e}")
        return None


def log_multiplication_to_s3(
    user_input: float,
    multiplier: float,
    product: float,
    name: str,
    explanation: str,
    latency_ms: float,
    client_ip: str,
    bucket: str = S3_BUCKET,
    object_key: str = LOG_CSV_KEY,
) -> None:
    """Append a multiplication log row to S3."""
    s3 = boto3.client("s3")

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

    try:
        obj = s3.get_object(Bucket=bucket, Key=object_key)
        existing_df = pd.read_csv(io.BytesIO(obj["Body"].read()))
        df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)
    except s3.exceptions.NoSuchKey:
        df = pd.DataFrame([new_row])
    except Exception as e:
        logger.warning(
            f"⚠️ Failed to load existing log from s3://{bucket}/{object_key}: {e}"
        )
        df = pd.DataFrame([new_row])

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    s3.put_object(Bucket=bucket, Key=object_key, Body=buffer.getvalue())
    logger.info(f"✅ Logged multiplication event to s3://{bucket}/{object_key}")
