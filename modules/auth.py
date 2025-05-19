import streamlit as st
import hashlib
import secrets
from modules.db_handler import DBHandler

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}${hashed.hex()}"

def verify_password(stored_password, provided_password):
    salt, hashed = stored_password.split('$')
    new_hash = hash_password(provided_password, salt)
    return new_hash == stored_password

def login_user(email, password):
    db = DBHandler()
    user = db.get_user_by_email(email)
    if user and verify_password(user[2], password):
        st.session_state.user = {
            'user_id': user[0],
            'email': user[1]
        }
        return True
    return False

def register_user(email, password):
    db = DBHandler()
    # Check if user exists
    if db.get_user_by_email(email):
        return False, "Email already registered"
    
    # Hash password
    password_hash = hash_password(password)
    
    # Create user
    try:
        db.create_user(email, password_hash)
        return True, "Registration successful"
    except Exception as e:
        return False, str(e)

def check_authenticated():
    if 'user' not in st.session_state:
        st.session_state.user = None
    return st.session_state.user is not None

def logout_user():
    st.session_state.user = None
    