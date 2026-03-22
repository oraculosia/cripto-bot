import base64
import json
from pathlib import Path
import streamlit as st


@st.cache_resource(show_spinner=False)
def img_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


@st.cache_resource(show_spinner=False)
def load_lottie_local(filepath):
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


@st.cache_resource(show_spinner=False)
def load_json(filepath):
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)
