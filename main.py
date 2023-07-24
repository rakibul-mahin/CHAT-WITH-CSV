import streamlit as st
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
from dotenv import load_dotenv
import os

def main():
    # load_dotenv()
    st.set_page_config(page_title="Chat with your CSV 📊")
    st.header("Chat with your CSV 📊")
    
    with st.sidebar:
        openai_api_key = st.text_input(label="Enter your OpenAI API key 👇", placeholder="sk-", type="password")
        csv_file = st.file_uploader("Upload your CSV file here", type="csv")
        
    if csv_file is not None and openai_api_key is not None:
        
        os.environ["OPENAI_API_KEY"] = str(openai_api_key)

        agent = create_csv_agent(
            OpenAI(temperature=0),
            csv_file.name, verbose=True
        )

        user_question = st.text_input("Ask a question about your CSV: ")

        if user_question is not None and user_question != "":
            with st.spinner(text="In progress..."):
                st.write(agent.run(user_question))


if __name__ == '__main__':
    main()