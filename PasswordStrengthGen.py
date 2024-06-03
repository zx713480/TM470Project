# Imports
import string
import random
import streamlit as st
import joblib
import sklearn


# Tokenizer for password vectorizer
def getTokens(inputString):
    tokens = []
    for i in inputString:
        tokens.append(i)
    return tokens



# Loads the machine learning model
def load_model():
    with open('/Users/charlie/Documents/GitHub/TM470Project/data/model', 'rb') as model:
        loaded_model = joblib.load(model)
    return loaded_model



def load_vectorizer():
    with open('/Users/charlie/Documents/GitHub/TM470Project/data/password_v', 'rb') as password_vec:
        password_v = joblib.load(password_vec)
    return password_v


# Function that generates a strong password of length 'length' when called
def generate_strong_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password


# Containers
title = st.container()
strength_check = st.container()
password_gen = st.container()

# Title of webpage
with title:
    st.title("Password Strength Checker and Generator :key:")
    st.write("""
    This application helps you to check the strength of your password and generate a strong password.
    It uses the power of machine learning and AI to predict the strength of your password.
    """)

# Password strength checker
with strength_check:
    st.header("Check Password Strength")
    input_password = st.text_input("Input your password", type="password")
    prediction = load_model()
    vectorizer = load_vectorizer()

    # If the button is clicked, the loaded ML model will predict the inputted password
    # and produce an output
    if st.button("Check"):
        vect_pswd = vectorizer.transform([input_password]).toarray()
        prediction_output = prediction.predict(vect_pswd)
        if prediction_output == 0:
            st.error("Weak")
        elif prediction_output == 1:
            st.warning("Medium")
        else:
            st.success("Strong")


# Generates a password
with password_gen:
    st.header("Generate Strong Password")
    password_length = st.slider("Password Characters", min_value=12, max_value=25, step=1)
    if st.button("Generate"):
        strong_password = generate_strong_password(password_length)
        st.write("Your generated password: \n", strong_password)
