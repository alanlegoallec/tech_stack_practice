#!/usr/bin/env python3
"""
Upload a CSV to S3 using boto3.
Make sure you have AWS credentials configured via:
  - `aws configure` OR
  - environment variables (AWS_ACCESS_KEY_ID, etc.)
"""

import os
import random

import boto3
import pandas as pd

# === Config ===
BUCKET_NAME = "fullstack-practice-data"
OBJECT_NAME = "uploads/names_and_numbers.csv"  # Can include folders
LOCAL_FILENAME = "names_and_numbers.csv"
LOCAL_PATH = "data/"


def create_dataframe(filename: str):
    """Generate a sample DataFrame with typical names and save to CSV."""
    names = [
        "Alice",
        "Bob",
        "Charlie",
        "Diana",
        "Ethan",
        "Fiona",
        "George",
        "Hannah",
        "Isaac",
        "Julia",
    ]
    df = pd.DataFrame(
        {
            "name": random.sample(names, k=10),
            "number": [random.randint(1, 1000) for _ in range(10)],
        }
    )
    df.to_csv(filename, index=False)
    print(f"✅ CSV written to {filename}")


def upload_file_to_s3(local_file: str, bucket: str, object_name: str):
    """Upload a local file to an S3 bucket."""
    session = boto3.Session(profile_name="deployer-full-stack-practice")
    s3 = session.client("s3")
    try:
        s3.upload_file(local_file, bucket, object_name)
        print(f"✅ Uploaded to s3://{bucket}/{object_name}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")


if __name__ == "__main__":
    # Ensure script is run from project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
    create_dataframe(f"{LOCAL_PATH}_{LOCAL_FILENAME}")
    upload_file_to_s3(LOCAL_FILENAME, BUCKET_NAME, OBJECT_NAME)
