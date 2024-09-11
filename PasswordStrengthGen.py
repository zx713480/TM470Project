# Imports
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


# Loads the word list used to generate passphrases.
# Caches the word list so the webpage only has to load it the once. This reduces
# the work load of the webpage.
@st.cache_data
def load_words():
    with open("data/English_Words.txt", "r") as words:
        word_list = words.read().split()
    return word_list


# Loads the machine learning model ready to be used by the website.
@st.cache_data
def load_model():
    with open('data/model', 'rb') as model:
        loaded_model = joblib.load(model)
    return loaded_model


# Loads the vectoriser that allows the machine learning model to work
@st.cache_data
def load_vectorizer():
    with open('data/password_v', 'rb') as password_vec:
        password_v = joblib.load(password_vec)
    return password_v


# Function that generates a strong password of length 'length' when called
def generate_strong_password(length):
    # Stores ascii letters, digits and punctuation in variable "characters"
    characters = string.ascii_letters + string.digits + string.punctuation
    # Stores n number of random characters of size "length-4" into variable "password"
    password = ''.join(random.choice(characters) for i in range(length - 4))
    # Adds a punctuation character, uppercase, lowercase letter and a digit to ensure
    # the password meets the requirements
    password += (random.choice(string.punctuation) + random.choice(string.ascii_uppercase) +
                 random.choice(string.ascii_lowercase) + random.choice(string.digits))

    return password


# Gives the inputted password a score based on certain metrics.
# This score is used to generate a strength bar under the password.
def password_strength_for_strength_bar(password):
    length = len(password)
    score = 0

    if length >= 12:
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


# Provides a colour for the password strength bar, weak is red, medium is orange, strong is green
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
information = st.container()

# Provides a sidebar for the webpage so the user can select between 2 pages.
page = st.sidebar.radio('Choose:', ['Strength Check and Password Gen', 'More Info'])

# If the user has selected 'Strength Check and Password Gen' this page will show.
if page == 'Strength Check and Password Gen':
    # Title of webpage
    with title:
        st.title(":lock: Password Strength Checker & Generator")
        # Provides dropdown menu with explanation of website and disclaimer
        with st.expander('About this app'):
            st.write("This application helps you to check the strength of your password using the power of machine "
                     "learning and AI. It can also create a strong password or passphrase for you.")
            st.markdown('**How To Use This App**')
            st.markdown('***Checking Password Strength***')
            st.info('To check the strength of your password, enter it into the \"Check Password Strength\" input field '
                    'below. Once done so, click \"check\" to have your password put to the test against our strength '
                    'checker!')
            st.markdown('***Password/Passphrase Generator***')
            st.info('To generate a strong password or passphrase, use the dropdown list to select which option you\'d '
                    'like to choose. Once you\'ve decided, use the slider to select the length of your pass-word\phrase'
                    ' and click \"Generate\".')

            st.markdown('**Disclaimer**')
            st.warning("This application does not store any information about you, nor does it store your inputted or "
                       "generated pass-words/phrases. The sole purpose of this website is to provide you with a free "
                       "service where you can check the strength of your password and to generate a password or phrase "
                       "if you need help with creating one.")
            st.markdown('***To Learn More***')
            st.info("If you would like to learn more about the importance of having a strong password and how to "
                    "maintain good password hygiene click on the arrow at the top left of the webpage and go "
                    "to \'More Info\'")

        st.write("Welcome to my password strength checker and generator! This application will help you to check the "
                 "strength of your password using the power of machine learning and AI!")
        st.write("It will also help you to generate a strong password or passphrase for you to use to help prevent "
                 "hackers from cracking your password! ")



    # Password strength checker
    with strength_check:
        prediction = load_model()
        vectorizer = load_vectorizer()

        st.header("Check Password Strength")
        input_password = st.text_input("Input your password", type="password")

        # If the button is clicked, the loaded ML model will predict the inputted password
        # and produce an output
        if st.button("Check"):
            result = ''
            # First checks if the password is in the data.csv file which is the file the model was trained on.
            # This is to make sure that the user isn't using a password that has already been leaked.
            with open('/Users/charlie/Documents/TM470Project/data/data.csv') as file:
                contents = file.read()
                # Tells the user if their password is in the data leak file
                if input_password in contents:
                    prediction_output = 0
                    st.error("This password was found to be in a data leak.")
                else:
                    # passes the users password to the ML model and returns a strength rating.
                    vect_pswd = vectorizer.transform([input_password]).toarray()
                    prediction_output = prediction.predict(vect_pswd)
            # outputs weak if the ML model returns a strength rating of 0
            if prediction_output == 0:
                result = 'Weak'
                st.error("Weak")
                st.markdown("Please go to the \'More Info\' page to learn how to create a strong password.")
            # outputs medium if the ML model returns a strength rating of 1
            elif prediction_output == 1:
                result = 'Medium'
                st.warning("Medium")
                st.markdown("Getting there! Please go to the \'More Info\' page to learn how to create a "
                            "stronger password.")
            # outputs strong if the ML model neither returns 0 nor 1. I.e. if the model returns 2.
            else:
                result = 'Strong'
                st.success("Strong")
                st.markdown("That's a great password! If you'd like to learn more about strong passwords, "
                            "please go to the \'More Info\' page to learn more.")

            # Gets the score from password_strength_for_strength_bar
            score = password_strength_for_strength_bar(input_password)
            # Fills the strength bar to a certain percentage based on the score above
            st.markdown(
                f"""
                <div class="password-strength-bar {result}" style="width: {score * 20}%;"></div>
                """,
                unsafe_allow_html=True
            )
            # Checks if the inputted password has certain features, puts a tick or cross next to each feature it has
            # or hasn't got. Outputs the results to the webpage.
            st.markdown("### Password Tips:")
            st.markdown(f"- {':heavy_check_mark:' if len(input_password) >= 12 else ':x:'} Use more characters")
            st.markdown(f"- {':heavy_check_mark:' if re.search('[a-z]', input_password) else ':x:'} Use lowercase letters")
            st.markdown(f"- {':heavy_check_mark:' if re.search('[A-Z]', input_password) else ':x:'} Use uppercase letters")
            st.markdown(f"- {':heavy_check_mark:' if re.search('[0-9]', input_password) else ':x:'} Add numbers")
            st.markdown(f"- {':heavy_check_mark:' if re.search('[@#$%^&+=]', input_password) else ':x:'} Add special characters")


    # Generates a password or passphrase
    with password_gen:
        # Title
        st.header("Generate Strong Password")
        # Creates a dropdown menu for the user to select password or passphrase creation
        password_choice = st.selectbox('Please select whether you\'d like to create a multi-character password, or '
                                       'multi-phrase passphrase.', ['Password', 'Passphrase'])
        # Password generation
        if password_choice == 'Password':
            # Creates a slider to allow the user to select the length of password.
            # Minimum length of 12 characters, max of 25, in increments of 1.
            password_length = st.slider("Number of Characters", min_value=12, max_value=25, step=1)
            # Creates a button that creates the password once clicked
            if st.button("Generate"):
                # Calls the 'generate_strong_password' function
                strong_password = generate_strong_password(password_length)
                st.success("Your generated password:")
                # Displays the password in a code block. This provides the user a 'copy' function that
                # the user can use to copy the password.
                st.code(strong_password, language='')
        # Passphrase generation
        if password_choice == 'Passphrase':
            # Loads a word list
            words = load_words()
            # Creates a slider to allow the user to select the number of words in the passphrase.
            # Minimum number is 3, max is 8, increments of 1.
            passphrase_length = st.slider("Number of Words", min_value=3, max_value=8, step=1)
            # Creates a button that generates the passphrase once clicked.
            if st.button("Generate"):
                # empty string
                strong_passphrase = ""
                # loops 'passphrase_length - 1' because I want a dash between each word but not on the final word.
                for i in range(passphrase_length -1 ):
                    # 'random.choice' will select a random word from the word list
                    # this random word will be appended to 'strong_passphrase' with a dash.
                    strong_passphrase += random.choice(words) + "-"
                # adds the last word to the passphrase without a dash
                strong_passphrase += random.choice(words)
                st.success("Your generated passphrase:")
                st.code(strong_passphrase, language='')
# if the user has selected 'More info', this page will show
if page == 'More Info':
    # title
    st.header("Information on Password Security")
    # information for the user
    st.write("Passwords are an essential part system security, and having a weak password"
             " is one of the most common causes of data breaches. Passwords protect your electronic "
             "accounts and devices from unauthorised access. ")
    # drop-down box with info on what makes up a strong password
    with st.expander("**What makes up a strong password?**", expanded=False):
        st.markdown(
            """
            According to [Microsoft](https://support.microsoft.com/en-gb/windows/create-and-use-strong-passwords-c5cebb49-8c53-4f5e-2bc4-fe357ca048eb) a strong password must: 
            - Be at least 12 characters long.
            - A combination of uppercase and lowercase letters, numbers, and symbols.
            - Not a word that can be found in a dictionary or the name of a person, character, product or organisation.
            - Significantly different from your previous passwords.
            - Easy for you to remember but difficult for others to guess. Consider using a memorable phrase like \'6MonkeysRLooking^\'.
            """
        )
    # drop down box with info on how to keep passwords secure
    with st.expander("**How to keep your passwords secure**", expanded=False):
        st.markdown(
            """
            To keep your passwords secure:
            - Dont share them with anyone.
            - Never send a password by email, instant message, or any other communication platform that is not reliably secure.
            - Use a unique password for each website. 
            - If you don't want to memorize multiple passwords, consider using a password manager. 
            - Consider writing down a hint that reminds you of what the password is.
            """
        )
        # adds hyperlink
        st.markdown("Find out more [here](https://support.microsoft.com/en-gb/windows/create-and-use-strong-passwords-c5cebb49-8c53-4f5e-2bc4-fe357ca048eb)")
    # drop down box
    with st.expander("**The risks with weak passwords**", expanded=False):
        st.markdown(
            """
            - ###### Unauthorised Access
            Having weak passwords makes your online accounts vulnerable to unauthorized access. If an intruder gaines 
            access, they can extract sensitive information, impersonate the legitimate user, or disrupt operations. 
            - ###### Data Breaches
            When attackers gain access to one account, they can often navigate through an entire network, accessing 
            confidential data which they can sell online to malicious actors or rival companies. 
            - ###### Identity Theft
            Identity theft often begins with a single compromised password. Attackers can use the stolen credentials 
            to impersonate individuals, apply for credit, or engage in fraudulent activities, all under another person's name. 
            - ###### Financial Losses 
            In a business context, a breaches account can lead to stolen funds or intellectual property, 
            costing companies millions. For individuals, the theft of banking or credit card information can have
            immediate and devastating financial implications.
            - ###### Others
            To learn about more risks associated with weak passwords, alongside common password cracking techniques, 
            password best practices and more, please visit Jetpack [here](https://jetpack.com/blog/weak-passwords)
            """
        )

    with st.expander("**Why choose a passphrase over a password?**", expanded=False):
        st.markdown(
            """
            - Passwords tend to be around 8 characters long, whereas passphrases tend to be a much longer 16-32 characters long. 
            And even with this added length, they are much easier to remember. The added length of a passphrase makes these much harder
            for threat actors to attack, making them the stronger choice. 
            - Secure passwords tend to be quite complex, making them hard to remember. This has resulted in 13% of Americans using the same 
            password for every account they own, and 35% of individuals never changing their passwords. This is a clear security risks for
            individuals and companies. However, adopting techniques such as passphrases instead of one-word
            passwords is an easy way to improve your cybersecurity posture and defend against potential attacks. 
            
            To find out more, please visit: [DOT Security](https://dotsecurity.com/insights/blog-are-passphrases-more-secure-than-passwords)
            
            """
        )
