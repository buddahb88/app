import streamlit as st
import os
import openai
import base64
from PIL import Image

def openai_chat_completion(messages):
    openai.api_key = os.getenv("AZURE_OPENAI_KEY")
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_type = 'azure'
    openai.api_version = '2023-05-15' 

    deployment_name='AI_AmplifyCP'

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        engine=deployment_name,
        messages=messages,
        temperature=0.3,
        max_tokens=4096,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)

    return completion

def get_download_link(text, filename, link_text):
    b64_text = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64_text}" download="{filename}">{link_text}</a>'


def convert_code(source_code, source_lang, target_lang):
    start_phrase = f'''You are an AI assistant specializing in code conversions.
                       These are the languages that we will be converting to and from
                       'Teradata','SQL','Snowflake SQL','Python', 'JavaScript', 'PySpark','Snowpark'

                       Abide by these rules below
                       1. If {target_lang} is Snowflake SQL
                       be sure to return the converted code as a snowflake stored procedure with the language being SQL
                       monitor temp tables that begin with  a "#" and flag those as temporary tables. Otherwise the table creation 
                       should be treated as a permanent table and should begin with CREATE OR REPLACE TABLE. Also, any creation of temp tables or permanent tables
                       with DROP TABLE IF EXISTS then the conversion should begin with "CREATE OR REPLACE" as is standard
                       with Snowflake. 
                       2.  If the code is too long to return, instruct the user to Shorten the code into smaller chunks for
                           better conversion results 
                       3.  After taking the previous rules into consideration, 
                       Convert the code below from  {source_lang} to {target_lang}
                       Here is the code to be converted: {source_code}'''
    
    
    st.session_state['last_message'] = {"role": "user", "content": start_phrase}

    completion = openai_chat_completion([st.session_state['last_message']])

    desired_text = completion.choices[0].message.content
    
    return completion, f'// Converted code from {source_lang} to {target_lang}.\n\n{desired_text}'

def provide_summary(source_code):
    start_phrase = f''' You are an AI assistant specializing in code summaries.
                        Could you provide me a detailed summary of what this source code does: {source_code}
                        If the code is in SQL, could you provide a text chart of what db's, 
                        schemas and tables and dependencies that are involved, 
                        and also what the code is actually doing'''


    st.session_state['last_message'] = {"role": "user", "content": start_phrase}

    completion = openai_chat_completion([st.session_state['last_message']])

    desired_text = completion.choices[0].message.content

    return desired_text

def main():
    logo = Image.open("logo.jpg")
    code_logo = Image.open("code_tools.png")

    st.set_page_config(page_title='Amplify Code Tools',
                      page_icon=logo,
                      layout='wide',
                      initial_sidebar_state='auto')

    st.sidebar.image(code_logo)
    st.sidebar.info(
            """
            ## Code Conversion Tool
            1. Provide the Source Code in the 'Source Code' area.
            2. Select the Source Language from the dropdown menu.
            3. Select the Target Language from the dropdown menu.
            4. Click the 'Convert' button to initiate the conversion process.
            5. The converted code will be displayed in the 'Converted Code' section.
            """
    )
    
    st.sidebar.info(
            """
            ## Code Summary Tool
            1. Provide the Source Code in the 'Source Code' area.
            2. Press "Get Code Summary" button.
            3. Export your summary by pressing "Download Code Summary" button.
            """
    )

    st.markdown("<h1 style='text-align: center;'>Amplify Code Tools (POC's)</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Code Conversion Tool", "Code Summary Tool"])

    with tab1:
        st.markdown("<h2 style='text-align: center;'>Code Conversion Tool</h2>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: left;'>Source Code:</h3>", unsafe_allow_html=True)
        source_code = st.text_area("", label_visibility="hidden",height=300)
        col1, col2 = st.columns(2)
        with col1:
            source_lang = st.selectbox('Select Source Language', options=['Teradata','SQL','Snowflake SQL','Python', 'JavaScript', 'PySpark','Snowpark'])
        with col2:
            target_lang = st.selectbox('Select Target Language', options=['Teradata','SQL','Snowflake SQL','Python', 'JavaScript', 'PySpark','Snowpark'])

        if st.button("Convert"):
            if source_code:
                previous_conversion, converted_code = convert_code(source_code, source_lang, target_lang)
                st.session_state['previous_conversion'] = previous_conversion
                st.markdown("<h3 style='text-align: left;'>Converted Code:</h3>", unsafe_allow_html=True)
                st.text_area("",value=converted_code,label_visibility="hidden",height=300)
            else:
                st.warning('Please enter some source code to convert.')

    with tab2:
        st.markdown("<h2 style='text-align: center;'>Code Summary Tool</h2>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: left;'>Source Code:</h3>", unsafe_allow_html=True)
        source_code = st.text_area("",height=300,key=2)

        if st.button("Get Code Summary"):
            if source_code:
                code_summary = provide_summary(source_code)
                st.text_area("",value=code_summary,label_visibility="hidden",height=300,key=3)

                if st.download_button("Download Code Summary",data=code_summary,mime='text/plain'):
                    st.success("Code Summary Downloaded!")
            else:
                st.warning('Please enter some code to get a summary')

        
        
if __name__ == "__main__":
    main()
