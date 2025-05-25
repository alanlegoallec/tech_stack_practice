import boto3
import pandas as pd
import time
import uuid
import requests
from io import BytesIO

BUCKET = "fullstack-practice-data"
OBJECT_KEY = "outputs/multiplication_log.csv"
BACKEND_URL = "https://api.alg-fullstackpractice.top/multiply"

def get_csv_from_s3(bucket, key):
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(BytesIO(obj["Body"].read()))

def test_s3_logging_works():
    # === Step 1: Read existing log (or empty)
    try:
        df_before = get_csv_from_s3(BUCKET, OBJECT_KEY)
        num_rows_before = len(df_before)
    except Exception:
        num_rows_before = 0

    # === Step 2: Trigger a multiply request
    payload = {"number": 7}
    response = requests.post(BACKEND_URL, json=payload)
    assert response.status_code == 200

    # === Step 3: Wait and read updated CSV
    time.sleep(2)  # wait for write to propagate
    df_after = get_csv_from_s3(BUCKET, OBJECT_KEY)
    num_rows_after = len(df_after)

    # === Step 4: Confirm row was added
    assert num_rows_after == num_rows_before + 1, (
        f"Expected {num_rows_before + 1} rows, found {num_rows_after}"
    )

    new_row = df_after.iloc[-1]
    assert new_row["user_input"] == 7
    assert new_row["product"] == new_row["user_input"] * new_row["random_multiplier"]
    assert isinstance(new_row["associated_name"], str)
    assert isinstance(uuid.UUID(new_row["request_id"]), uuid.UUID)
