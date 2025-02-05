import os
from dotenv import load_dotenv
import openai
import requests
import json

import time
import logging
from datetime import datetime
import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]

load_dotenv()

client = openai.OpenAI()
model = "gpt-4-turbo"
#"gpt-4-1106-preview"  
#"gpt-3.5-turbo"
#"gpt-4o"
#"gpt-4-turbo"

# # Read the instruction file
# with open('2correctorincorrect.txt', 'r') as file:
#     instructions_data = file.read()

#read instruction file from streamlit secrets
instructions_data = st.secrets["INSTRUCTIONS"]

#  == Hardcoded ids to be used once the first code run is done and the assistant was created
assis_id = "asst_pZOBXOqtGYnQwd8LWiak5iRn" 
thread_id = "thread_lClMjq57Qa4Dt2bzptzTmhAq"

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

st.set_page_config(page_title="Jay ChatBot", page_icon=":books:")
#st.set_page_config(page_title="Study Buddy", page_icon=":books:")


if st.button("Start Chat"):
    st.session_state.start_chat = True
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

st.title("J-bot")
st.image("Jay Chatbot Image.jpg")
st.write("How can I help you with History 1301?")
# st.write("Ask me things like:")
# st.write(":blue[**Explain Module 1 Quiz 2 question 3**] OR :blue[**Help solve module 3 Quiz 1 question 3**] OR :blue[**copy-paste the question after clicking Start Chat**]")
st.write(":blue[**Click Start Chat and copy-paste or type the question in**]")

if st.button("Clear Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state
    st.session_state.thread_id = None

if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter message"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=prompt
            )
        
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assis_id,
            instructions=instructions_data
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.markdown(message.content[0].text.value)
                #st.markdown(message.content[0].text.value, unsafe_allow_html=True)

else:
    st.write("Click 'Start Chat' to begin.")
        


