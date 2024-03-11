import streamlit as st
import time
from src.services.user_service import UserManager

class Auth:
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    def display_forms(self):
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
        with tab_login:
            self._login_form()
        with tab_signup:
            self._signup_form()

    def _login_form(self):
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type='password', key="login_password")
        if st.button("Login"):
            success, user_id = self.user_manager.validate_login(username, password)
            if success:
                st.session_state['user_id'] = user_id
                st.success(f"Successfully logged in as {username}")
                with st.spinner('Loading... Please wait.'):
                    time.sleep(2) 
                st.rerun()
            else:
                st.error("Invalid username or password.")

    def _signup_form(self):
        st.subheader("Sign Up")
        username = st.text_input("Choose Username", key="signup_username")
        password = st.text_input("Choose Password", type='password', key="signup_password")
        confirm_password = st.text_input("Confirm Password", type='password', key="confirm_password")
        email = st.text_input("Email", key="signup_email")
    
        if st.button("Register"):
            # Check if passwords match
            if password == confirm_password:
                # Proceed with registration if passwords match
                success, message = self.user_manager.register_user(username, password, email)
                if success:
                    st.success("Account created successfully! You can now login.")
                else:
                    st.error(message)
            else:
                # If passwords don't match, display an error message
                st.error("Passwords do not match. Please try again.")
