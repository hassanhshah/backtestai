import hashlib
import mysql.connector
from datetime import datetime

from src.database.connection import get_db_connection

class UserManager:
    def __init__(self):
        self.db_connection = get_db_connection()
        self.cursor = self.db_connection.cursor()
        
    def register_user(self, username, password, email):
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if self.username_exists(username):
            return False, "Username already taken. Please choose a different one."
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        query = "INSERT INTO User (username, password, email) VALUES (%s, %s, %s)"
        try:
            self.cursor.execute(query, (username, hashed_password, email))
            self.db_connection.commit()
            return True, "User successfully registered."
        except mysql.connector.Error as err:
            return False, f"Failed to register user: {err}"
        
    def username_exists(self, username):
        """Check if a username already exists in the database."""
        query = "SELECT COUNT(*) FROM User WHERE username = %s"
        self.cursor.execute(query, (username,))
        count = self.cursor.fetchone()[0]
        return count > 0
        
    def validate_login(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        query = "SELECT user_id, password FROM User WHERE username = %s"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        if result and result[1] == hashed_password:
            update_status, update_message = self.update_last_login(result[0])
            if update_status:
                return True, result[0]
            else:
                return False, update_message
        return False, None
    
    def update_last_login(self, user_id):
        """
        Updates the last_login column for a given user_id with the current timestamp.
        """
        query = "UPDATE User SET last_login = %s WHERE user_id = %s"
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            self.cursor.execute(query, (current_time, user_id))
            self.db_connection.commit()
            return True, "Last login updated successfully."
        except mysql.connector.Error as err:
            return False, f"Failed to update last login: {err}"
        
    def close(self):
        self.cursor.close()
        self.db_connection.close()