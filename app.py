import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import re
import sympy as sp

# --- Helper Functions ---
def preprocess_image(image):
    img = image.convert('L')  # Convert to grayscale
    img = img.resize((800, 600))
    return img

def clean_expression(expression):
    expression = expression.lower()
    replacements = {
        "sine": "sin", "cosine": "cos", "tangent": "tan",
        "logarithm": "log", "square root": "sqrt",
        "times": "*", "into": "*", "divided by": "/",
        "power": "**", "raise to": "**"
    }
    for word, symbol in replacements.items():
        expression = expression.replace(word, symbol)
    expression = re.sub(r'[^0-9+\-*/().a-z^]', '', expression)
    return expression

def calculate_expression(expression):
    if not expression:
        return "No valid expression detected."
    try:
        result = sp.sympify(expression)
        return f"Extracted Expression: {expression}\nResult: {result.evalf()}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

# --- Streamlit App ---
st.set_page_config(page_title="Math Expression Evaluator", page_icon="➗")
st.title("➗ Math Expression Evaluator")

option = st.sidebar.radio("Choose Input Method:", ("Type Expression", "Upload Image"))

# --- 1. Type Expression ---
if option == "Type Expression":
    user_input = st.text_input("Enter a math expression:")
    if user_input:
        expr = clean_expression(user_input)
        st.success(calculate_expression(expr))

# --- 2. Upload Image (OCR functionality removed for now) ---
elif option == "Upload Image":
    st.write("Image-to-text extraction (OCR) is disabled in this version.")
    uploaded_file = st.file_uploader("Upload an image (feature disabled):", type=['jpg', 'jpeg', 'png'])

# Footer
st.markdown("---\nMade for deployment environments without Tesseract or eSpeak.")
