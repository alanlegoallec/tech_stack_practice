import streamlit as st
import requests

st.title("Multiply by a random number")

number = st.number_input("Enter a number:", min_value=0, value=1)
if st.button("Multiply"):
    # Call the Flask API
    response = requests.post(
        "http://backend-app:5001/multiply",  # Use the service name as the host (see Docker Compose below)
        json={"number": number}
    )
    if response.ok:
        result = response.json()["result"]
        explanation = response.json()["explanation"]
        st.success(f"Result: {result}; explanation: {explanation}")
    else:
        st.error("Error contacting Flask API.")
