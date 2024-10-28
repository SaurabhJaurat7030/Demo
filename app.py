# Importing important libraries
import pandas as pd
from transformers import DistilBertTokenizer, DistilBertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker


# Loading and Cleaning the data
df = pd.read_excel('QesAnsPairs.xlsx')
df = df.dropna(subset=['questions', 'answers'])
df['questions'] = df['questions'].astype(str)
df['answers'] = df['answers'].astype(str)

# Loading DistilBERT model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertModel.from_pretrained('distilbert-base-uncased')

# Encoding the questions
def encode_questions(questions):
    inputs = tokenizer(questions, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].numpy()

question_embeddings = encode_questions(df['questions'].tolist())

#-------------------**********---------------------#
# user_input = input("give your input")

# user_embedding = encode_questions([user_input])

# # Step 6: Calculate cosine similarity
# similarities = cosine_similarity(user_embedding, question_embeddings)

# # Step 7: Identify the most similar question
# most_similar_index = similarities.argmax()

# response = df['answers'].iloc[most_similar_index]

# print(response)
#-------------------**********---------------------#
engine = create_engine('sqlite:///user.db')  # Change this path as needed
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()

# Define the User table (for demo purposes, password stored as plain text)

questions_table = Table('questions', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('question', String, nullable=False )
)

# Create the table if it doesn't exist
metadata.create_all(engine)

def add_question(response):
    session.execute(questions_table.insert().values(question=response))
    session.commit()
    return True

# Building Streamlit app
st.title("🌨️ LearnBuddy")
st.markdown("<p style='color:gray; font-style:italic;'>Ask questions and get instant answers on functional testing, business cases, and more!</p>", unsafe_allow_html=True)

# initiating message dictionary
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display of the chat messages from history
for message in st.session_state["messages"]:
    if message["role"] == "assistant":
        col1, col2 = st.columns([5, 1])
        with col1:
            st.chat_message("assistant").markdown(message["content"])
    else:
        col1, col2 = st.columns([1, 5])
        with col2:
            st.chat_message("user").markdown(message["content"])

# taking the input promt from the user
prompt = st.chat_input("How can I help you today")

if prompt: 
    col1, col2 = st.columns([1, 5])
    with col2:
        st.chat_message("user").markdown(prompt)

    # Adding user message to chat history dictionary
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Encoding the user input 
    user_embedding = encode_questions([prompt])

    # finding the similarities between the features
    similarities = cosine_similarity(user_embedding, question_embeddings)
    most_similar_index = similarities.argmax()
    response = df['answers'].iloc[most_similar_index]

    # Display of the assistant response
    col1, col2 = st.columns([5, 1])
    with col1:
        st.chat_message("assistant").markdown(response)
        success = False
        if st.button("Not Satisfied?"):
             success = add_question(prompt)
        
        if success:
            st.warning("Your feedback has been recorded successfully!")
        # else:
        #     st.error("There was an error recording your feedback. Please try again.")


    # Adding assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
