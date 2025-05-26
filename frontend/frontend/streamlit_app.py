"""Streamlit app with auth support."""

import os

import requests
import streamlit as st

# 🌐 Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000").rstrip("/")

# --- Auth ---
st.sidebar.header("Login")

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    try:
        res = requests.post(
            f"{BACKEND_URL}/login",
            data={"username": username, "password": password},
            timeout=10,
        )
        res.raise_for_status()
        st.session_state["access_token"] = res.json()["access_token"]
        st.sidebar.success("Logged in!")
    except Exception as e:
        st.sidebar.error(f"Login failed: {e}")

# --- Multiply Form ---
st.title("Multiply BY a random number")
number = st.number_input("Enter a number:", min_value=0, value=1)

if st.button("Multiply"):
    if not st.session_state["access_token"]:
        st.error("You must log in first.")
    else:
        try:
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            response = requests.post(
                f"{BACKEND_URL}/multiply",
                json={"number": number},
                headers=headers,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            st.success(f"Result: {data['result']}; explanation: {data['explanation']}")
        except Exception as e:
            st.error(f"Error contacting backend: {e}")
