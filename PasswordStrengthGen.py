import string
import random
import streamlit as st
import joblib
import sklearn
import re


# Tokenizer for password vectorizer
def getTokens(inputString):
    tokens = []
    for i in inputString:
        tokens.append(i)
    return tokens

@st.cache_data
def load_words():
    with open("data/English_Words.txt", "r") as words:
        word_list = words.read().split()
    return word_list


@st.cache_data
# Loads the machine learning model
def load_model():
    with open('data/model', 'rb') as model:
        loaded_model = joblib.load(model)
    return loaded_model


@st.cache_data
def load_vectorizer():
    with open('data/password_v', 'rb') as password_vec:
        password_v = joblib.load(password_vec)
    return password_v


# Function that generates a strong password of length 'length' when called
def generate_strong_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def password_strength(password):
    length = len(password)
    score = 0

    if length >= 8:
        score += 1
    if re.search("[a-z]", password):
        score += 1
    if re.search("[A-Z]", password):
        score += 1
    if re.search("[0-9]", password):
        score += 1
    if re.search("[@#$%^&+=]", password):
        score += 1

    return score


st.markdown(
    """
    <style>
    .password-strength-bar {height: 10px; border-radius: 5px; background-color: #ddd; margin-top: 10px;}
    .Weak {background-color: red;}
    .Medium {background-color: orange;}
    .Strong {background-color: green;}
    </style>
    """,
    unsafe_allow_html=True
)


# Containers
title = st.container()
strength_check = st.container()
password_gen = st.container()

# Title of webpage
with title:
    st.title(":lock: Password Strength Checker & Generator")
    with st.expander('About this app'):
        st.write("This application helps you to check the strength of your password using the power of machine learning and AI"
                 "It can also create a strong password or passphrase for you.")
        st.markdown('**How to use this app**')
        st.markdown('***Checking password strength***')
        st.info('To check the strength of your password, enter it into the \"Check Password Strength\" input field below. '
                'Once done so, click \"check\" to have your password put to the test against our strength checker!')
        st.markdown('***Password/Passphrase Generator***')
        st.info('To generate a strong password or passphrase, use the dropdown list to select which option you\'d like to choose. '
                'Once you\'ve decided, use the slider to select the length of your pass-word\phrase and click \"Generate\".')

        st.markdown('**My promise to you**')
        st.warning("This application does not store any information about you nor does it store your inputted or generated pass-words/phrases.")
    st.write("""
    Welcome to my password strength checker and generator! This application will help you to check the strength of your password 
    using the power of machine learning and AI!""")
    st.write("It will also help you to generate a strong password or passphrase for you to use to help prevent hackers from cracking your password! ")



# Password strength checker
with strength_check:
    prediction = load_model()
    vectorizer = load_vectorizer()

    st.header("Check Password Strength")
    input_password = st.text_input("Input your password", type="password")

    # If the button is clicked, the loaded ML model will predict the inputted password
    # and produce an output
    if st.button("Check"):
        vect_pswd = vectorizer.transform([input_password]).toarray()
        prediction_output = prediction.predict(vect_pswd)
        result = ''
        if prediction_output == 0:
            result = 'Weak'
            st.error("Weak")
        elif prediction_output == 1:
            result = 'Medium'
            st.warning("Medium")
        else:
            result = 'Strong'
            st.success("Strong")

        score = password_strength(input_password)
        # Password strength bar
        st.markdown(
            f"""
            <div class="password-strength-bar {result}" style="width: {score * 20}%;"></div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### Password Tips:")
        st.markdown(f"- {':heavy_check_mark:' if len(input_password) >= 8 else ':x:'} Use more characters")
        st.markdown(f"- {':heavy_check_mark:' if re.search('[a-z]', input_password) else ':x:'} Use lowercase letters")
        st.markdown(f"- {':heavy_check_mark:' if re.search('[A-Z]', input_password) else ':x:'} Use uppercase letters")
        st.markdown(f"- {':heavy_check_mark:' if re.search('[0-9]', input_password) else ':x:'} Add numbers")
        st.markdown(f"- {':heavy_check_mark:' if re.search('[@#$%^&+=]', input_password) else ':x:'} Add special characters")


# Generates a password
with password_gen:
    st.header("Generate Strong Password")
    password_choice = st.selectbox('Please select whether you\'d like to create a multi-character password, or multi-phrase passphrase.', ['Password', 'Passphrase'])
    if password_choice == 'Password':
        password_length = st.slider("Number of Characters", min_value=12, max_value=25, step=1)
        if st.button("Generate"):
            strong_password = generate_strong_password(password_length)
            st.success("Your generated password:")
            st.code(strong_password, language='')
    if password_choice == 'Passphrase':
        words = load_words()
        passphrase_length = st.slider("Number of Words", min_value=3, max_value=8, step=1)
        if st.button("Generate"):
            strong_passphrase = ""
            for i in range(passphrase_length):
                strong_passphrase += random.choice(words) + " "
            st.success("Your generated passphrase:")
            st.code(strong_passphrase, language='')
