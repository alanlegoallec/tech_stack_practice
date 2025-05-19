"""Streamlit app."""

import os

import requests
import streamlit as st

# 🔁 Use BACKEND_URL env var for both local and prod
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000").rstrip(
    "/"
)  # fallback for local dev

st.title("Multiply BY a random number")

number = st.number_input("Enter a number:", min_value=0, value=1)

if st.button("Multiply"):
    try:
        response = requests.post(
            f"{BACKEND_URL}/multiply", json={"number": number}, timeout=60
        )
        response.raise_for_status()
        data = response.json()
        result = data["result"]
        explanation = data["explanation"]
        st.success(f"Result: {result}; explanation: {explanation}")
    except Exception as e:
        st.error(f"Error contacting backend: {e}")
