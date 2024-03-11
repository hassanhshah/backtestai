import mysql.connector
import streamlit as st

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        return conn
    except mysql.connector.Error as e:
        st.error("Database connection failed: " + str(e))
        raise e
