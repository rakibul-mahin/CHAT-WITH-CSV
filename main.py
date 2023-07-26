import streamlit as st
from langchain.agents import create_csv_agent, create_pandas_dataframe_agent
from langchain.llms import OpenAI
from dotenv import load_dotenv
import pandas as pd
import json
import os

def create_agent(filename):
    llm = OpenAI(temperature=0)
    df = pd.read_csv(filename)
    return create_pandas_dataframe_agent(llm, df, verbose=True, handle_parsing_errors=True)

def query_agent(agent, query):
    prompt = (
        """
            For the following query, if it requires drawing a table, reply as follows:
            {"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}

            If the query requires creating a bar chart, reply as follows:
            {"bar": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

            If the query requires creating a line chart, reply as follows:
            {"line": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

            There can only be two types of chart, "bar" and "line".

            If it is just asking a question that requires neither, reply as follows:
            {"answer": "answer"}
            Example:
            {"answer": "The title with the highest rating is 'Gilead'"}

            If you do not know the answer, reply as follows:
            {"answer": "I do not know."}

            Return all output as a string.

            All strings in "columns" list and data list, should be in double quotes,

            For example: {"columns": ["title", "ratings_count"], "data": [["Gilead", 361], ["Spider's Web", 5164]]}

            Lets think step by step.

            Below is the query.
            Query: 
        """
        + query
    )
    
    response = agent.run(prompt)
    return response.__str__()

def decode_response(response):
    return json.loads(response)

def write_response(response_dict):
    # Check if the response is an answer.
    if "answer" in response_dict:
        st.write(response_dict["answer"])

    # Check if the response is a bar chart.
    if "bar" in response_dict:
        data = response_dict["bar"]
        df = pd.DataFrame(data)
        df.set_index("columns", inplace=True)
        st.bar_chart(df)

    # Check if the response is a line chart.
    if "line" in response_dict:
        data = response_dict["line"]
        df = pd.DataFrame(data)
        df.set_index("columns", inplace=True)
        st.line_chart(df)

    # Check if the response is a table.
    if "table" in response_dict:
        data = response_dict["table"]
        df = pd.DataFrame(data["data"], columns=data["columns"])
        st.table(df)
    
    

def main():
    # load_dotenv()
    st.set_page_config(page_title="Chat with your CSV 📊")
    st.header("Chat with your CSV 📊")
    
    with st.sidebar:
        openai_api_key = st.text_input(label="Enter your OpenAI API key 👇", placeholder="sk-", type="password")
        option = st.selectbox("Plot Graphs?", ('Yes', 'No'))
        st.write(f"You have selected: {option}")
        csv_file = st.file_uploader("Upload your CSV file here", type="csv")
        
    if csv_file is not None and openai_api_key is not None:
        
        if option == "No":
            os.environ["OPENAI_API_KEY"] = str(openai_api_key)

            agent = create_csv_agent(
                OpenAI(temperature=0),
                csv_file.name, verbose=True
            )

            user_question = st.text_input("Ask a question about your CSV: ")

            if user_question is not None and user_question != "":
                with st.spinner(text="In progress..."):
                    st.write(agent.run(user_question))
        elif option == "Yes":
            os.environ["OPENAI_API_KEY"] = str(openai_api_key)
            user_question = st.text_input("Ask a question about your CSV: ")
            agent = create_agent(csv_file.name)
            response = query_agent(agent, user_question)
            decoded_response = decode_response(response)
            st.spinner()
            write_response(decoded_response)
            


if __name__ == '__main__':
    main()
    
# Create a bar graph on the first 5 rows