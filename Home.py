import streamlit as st
from hashing import hash_password, validate_hash
from app_model.db import get_connection
from app_model.users import add_user, get_user

conn = get_connection()


st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)

st.title("Welcome to the main page")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Only runs if logged in
with st.sidebar:
    st.header("👤 Profile")
    st.write(f"Username: {st.session_state.get('username', 'Unknown')}")
    st.write(f"Role: {st.session_state.get('role', 'Unknown')}")

    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state.pop('username', None)
        st.session_state.pop('role', None)
        st.switch_page("Home.py")  # redirect to login page

tab_login, tab_register = st.tabs(["Login", "Register"])

with tab_login:
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        user = get_user(conn, login_username)

        if user:
            username = user["username"]
            role = user["role"]
            password_hash = user["password_hash"]

            if validate_hash(login_password, password_hash):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['role'] = role

                st.success("Logged in successfully!")
                st.switch_page("pages/1_Dashboard.py")
            else:
                st.session_state['logged_in'] = False
                st.error("Incorrect password.")
        else:
            st.session_state['logged_in'] = False
            st.error("User not found.")
        

with tab_register:
    register_username = st.text_input("New Username")
    register_password = st.text_input("New Password", type="password")

    if st.button("Register"):
        st.session_state['logged_in'] = False
        try:
            add_user(conn, register_username, hash_password(register_password))
            st.success("User registered successfully!")
        except Exception as e:
            st.error(f"User already exists")
    
    else:
        st.info("Please fill in all the fields to register.")
