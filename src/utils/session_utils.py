import streamlit as st

class SessionUtils:
    @staticmethod
    def reset_session_state():
        exclude_keys = ['user_id']  # Keys not to reset
        keys_to_clear = [key for key in st.session_state.keys() if key not in exclude_keys]
        for key in keys_to_clear:
            del st.session_state[key]