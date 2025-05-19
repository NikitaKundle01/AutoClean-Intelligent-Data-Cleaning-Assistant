import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class DBHandler:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'autoclean_db'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', '')
            )
            if self.connection.is_connected():
                logging.info("Connected to MySQL database")
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("MySQL connection closed")
    
    def execute_query(self, query, params=None, fetch=False):
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            
            if fetch:
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.rowcount
        except Error as e:
            logging.error(f"Error executing query: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    # User operations
    def create_user(self, email, password_hash):
        query = "INSERT INTO users (email, password_hash) VALUES (%s, %s)"
        return self.execute_query(query, (email, password_hash))
    
    def get_user_by_email(self, email):
        query = "SELECT * FROM users WHERE email = %s"
        result = self.execute_query(query, (email,), fetch=True)
        return result[0] if result else None
    
    # File operations
    def log_file_upload(self, user_id, filename, filepath, filesize):
        query = """
        INSERT INTO file_uploads (user_id, original_filename, file_path, file_size)
        VALUES (%s, %s, %s, %s)
        """
        return self.execute_query(query, (user_id, filename, filepath, filesize))
    
    def log_cleaning_operation(self, upload_id, operation_type, details):
        query = """
        INSERT INTO cleaning_operations (upload_id, operation_type, operation_details)
        VALUES (%s, %s, %s)
        """
        return self.execute_query(query, (upload_id, operation_type, details))
    
    def log_cleaned_file(self, upload_id, clean_file_path):
        query = """
        INSERT INTO cleaned_files (upload_id, clean_file_path)
        VALUES (%s, %s)
        """
        return self.execute_query(query, (upload_id, clean_file_path))
    
    def get_user_files(self, user_id):
        query = """
        SELECT u.upload_id, u.original_filename, u.upload_time, 
               COUNT(c.operation_id) as operation_count,
               MAX(cf.clean_time) as last_cleaned
        FROM file_uploads u
        LEFT JOIN cleaning_operations c ON u.upload_id = c.upload_id
        LEFT JOIN cleaned_files cf ON u.upload_id = cf.upload_id
        WHERE u.user_id = %s
        GROUP BY u.upload_id
        ORDER BY u.upload_time DESC
        """
        return self.execute_query(query, (user_id,), fetch=True)