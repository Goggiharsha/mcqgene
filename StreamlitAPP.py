import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
from src.mcqgenerator.logger import logging
from src.mcqgenerator.utils import read_file,get_table_data
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.MCQgenerater import generate_evaluate_chain

with open("D:\mcqgene\Response.json") as file:
    RESPOENSE_JSON=json.load(file)
#loading json file for the app
st.title("MCQ CREATOR APPLICATION WITH LANGCHAIN")
#creat a from using st.from
with st.form("user_inputs"):
    #file upload
    uploaded_file=st.file_uploader("upload a PDF OR TXT file")

    #input Fileds
    mcq_count=st.number_input("no.of mcqs",min_value=3,max_value=50)

    #ssubject
    subject=st.text_input("insert subject",max_chars=20,)

    #quzitone
    tone=st.text_input("Complexity level of questions",max_chars=20,placeholder="simple")

    #add buton
    button=st.form_submit_button("create mcq")

    #chceck if the button clicked and all filed hane input
    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text=read_file(uploaded_file)
                #count tokens and the cost of api call
                with get_openai_callback as cb:
                    response=generate_evaluate_chain(
                        {
                            "text":text,
                            "number":mcq_count,
                            "subject":subject,
                            "tone":tone,
                            "response_json":json.dumps(RESPOENSE_JSON)
                        }
                    )
            except Exception as e:
                traceback.print_exception(type(e),e,e.__trackback__)
                st.error("error")
            else:
                print(f"Total Tokens:{cb.total_tokens}")
                print(f"Prompt Tokens:{cb.prompt_tokens}")
                print(f"Completion Tokens:{cb.completion_tokens}")
                print(f"Total Cost:{cb.total_cost}")
                if isinstance(response,dict):
                    quiz=response.get("quiz",None)
                    if quiz is not None:
                        table_data=get_table_data(quiz)
                        if table_data is not None:
                            df=pd.DataFrame(table_data)
                            df.index=df.index+1
                            st.table(df)
                            st.text_area(label="Review",value=response["Review"])
                        else:
                            st.error("error in the table")
                else:
                    st.write(response)
     