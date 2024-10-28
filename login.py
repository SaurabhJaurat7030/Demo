# Import necessary libraries
import streamlit as st
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
import subprocess
import datetime

# Database setup with SQLAlchemy (SQLite used here for simplicity)
engine = create_engine('sqlite:///users.db')  # Change this path as needed
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()

# Define the User table (for demo purposes, password stored as plain text)
users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True,autoincrement=True),
    Column('username', String, unique=True, nullable=False),
    Column('password', String, nullable=False),  # Plain text password (not secure)
)

questions_table = Table('questions', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('question', String, nullable=False )
)

# Create the table if it doesn't exist
metadata.create_all(engine)

# Function to add a user (used during registration)
def add_user(username, password):
    session.execute(users_table.insert().values(username=username, password=password))
    session.commit()

# Function to add the questions
def add_question(response):
    session.execute(questions_table.insert().values(question=response))
    session.commit()

# Function to check if username exists
def username_exists(username):
    query = session.query(users_table).filter_by(username=username).first()
    return query is not None

# Streamlit login and registration page
st.title("LearnBuddy")

# Button to toggle between Login and Register
if "show_register" not in st.session_state:
    st.session_state["show_register"] = False

if st.button("Go to Register" if not st.session_state["show_register"] else "Back to Login"):
    st.session_state["show_register"] = not st.session_state["show_register"]

# Registration Form
if st.session_state["show_register"]:
    st.header("Register New Account")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")

    if st.button("Register"):
        if username_exists(new_username):
            st.warning("Username already exists. Please choose a different one.")
        elif new_username and new_password:
            add_user(new_username, new_password)
            st.success("Registration successful! You can now log in.")
        else:
            st.warning("Please enter both a username and password.")

# Login Form
else:
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        
        query = session.query(users_table).filter_by(username=username, password=password).first()
        
        if query:
            st.success("Login successful!")
            subprocess.Popen(['streamlit', 'run', 'app.py'])
        else:
            st.error("Invalid username or password.")

