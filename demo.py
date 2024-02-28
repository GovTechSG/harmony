import streamlit as st


# UI Setup

description = st.text_input(label="Product Description", placeholder="Xbox 360 Motherboard")

if search := st.button("🔎 Search", type='primary'):
