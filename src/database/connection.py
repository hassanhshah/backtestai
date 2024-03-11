import mysql.connector
import streamlit as st

def get_db_connection():
    """
    This function creates and returns a new connection to the database.
    It also handles connection errors gracefully.
    """
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        return conn
    except mysql.connector.Error as e:
        # For a web application, you might want to show a user-friendly error message instead:
        st.error("Database connection failed: " + str(e))
        # In a script, you might prefer to raise the error to stop execution or to be caught by another layer of error handling
        raise e