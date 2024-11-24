import requests
import streamlit as st

st.title("Streamlit Frontend")

# Call the router function directly
from app.routers.data_router import get_data

response = get_data()
data = response.json()

st.write("Data from backend:")
st.json(data)
