"""Streamlit app."""

import os

import requests
import streamlit as st

backend_app_url_template = "http://backend-app:{port}/multiply"
backend_app_url = backend_app_url_template.format(port=os.environ.get("API_PORT"))
st.title("Multiply by a random number")

number = st.number_input("Enter a number:", min_value=0, value=1)
if st.button("Multiply"):
    # Call the Flask API
    response = requests.post(backend_app_url, json={"number": number}, timeout=60)
    if response.ok:
        result = response.json()["result"]
        explanation = response.json()["explanation"]
        st.success(f"Result: {result}; explanation: {explanation}")
    else:
        st.error("Error contacting Flask API.")
