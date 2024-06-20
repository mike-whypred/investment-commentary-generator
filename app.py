import streamlit as st
from openai import OpenAI
import base64
import os
from dotenv import load_dotenv
from streamlit_echarts import st_echarts
import re
from datetime import datetime
from streamlit_extras.colored_header import colored_header
import boto3
import json
import pandas as pd

# Function to read JSON file from S3
def read_json_from_s3(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')
    return json.loads(content)

def read_json_from_local(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

open_ai_key = st.secrets["OPENAI_API_KEY"]
os.environ['AWS_ACCESS_KEY_ID'] = st.secrets['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']   = st.secrets['AWS_SECRET_ACCESS_KEY']# Set API keys


# st.markdown(
#     """
#     <style>
#     .main { 
#         background-color: #FFFFFA; 
#     }
#     .stImage {
#         display: flex; 
#         justify-content: center;
#     }
#     h1 {
#         font-size: 36px;  /* Increase title size */
#     }
#     .caption {
#         font-size: 20px;  /* Increase caption size */
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# Initialize the S3 client
s3 = boto3.client('s3')

# Define the bucket name and file key
bucket_name = 'news-dumps'
file_key = 'news-report-current.json'

json_data = read_json_from_s3(bucket_name, file_key)

df = pd.DataFrame(json_data)

st.title("Commentary from Report")

st.caption("Upload performance table, set role, reporting date, add additional context/news")

st.header("Recent News")
st.dataframe(df)

with st.sidebar:
    
    colored_header(
        label="Commentary Generator",
        description="WhyPred",
        color_name="violet-70",
    )
    st.write('''Upload performance table, set role, reporting date, add additional context''')

# Dropdown for role selection
    role = st.selectbox("Select your role", ["Equity Portfolio Manager", "Multi-Asset Portfolio Manager", "Trader"])

# Date input
    report_date = st.date_input("Select reporting date", datetime.today())

# Free text input for market context
    market_context = st.text_area("Market Context")


    # news_context = st.file_uploader("Upload news report JSON", type=['json'])



    # if news_context is not None:
    # # Read the content of the file
    #     news_context = news_context.getvalue().decode("utf-8")
    
    # File uploader widget
    img_upload = st.file_uploader("Upload here...", type=["jpg", "jpeg", "png"])



    if role == "Trader":
        asset = "Spreads"
    elif role == "Equity Portfolio Manager":
        asset = "Equities"
    else:
        asset = "Equities"


    

if st.sidebar.button("Generate"):

    if img_upload is not None:
            # Display the uploaded image


        st.image(img_upload, caption='Uploaded Screenshot', use_column_width=True)


        # Read and encode the image in base64
        encoded_image = base64.b64encode(img_upload.read()).decode("utf-8")

    report_date = report_date.strftime("%Y-%m-%d")

    file_path = 'news-report-current.json'

# Function to read JSON file from local file system


# Read the JSON file
    #json_data = read_json_from_local(file_path)

# Convert the JSON data to a string
    news_string = json.dumps(json_data, indent=4)

    # Craft the prompt for GPT
    prompt_messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f'''Given the following investment performance report for different {asset} returns for the period ending {report_date} 
                                act as an experienced {role} and generate an interesting and insightful investment summary based on the report referencing numbers from the report. 
                                do not give anything else other than an insightful investment summary based on the report. Do not sound uncertain, be sure 
                                of what you're saying. Also refer to the following market context: {market_context} and the follow recent financial news :{news_string}. incoporate the 
                                news comprehensively in your summary. When backing up performance with news, explain the news instead of just referencing it.
                                 Interweave performance with the news, don't discuss them separately. When summarising don't make generic statements like
                                  "the market is a complex interplay of factors" summarise the key points in the summary. Do not provide recommendations or advice.
                                Also provide 10 potential nuanced and interesting
                                titles for the summary.


                            '''
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}"
                    }
                }
            ]
        }
    ]

    # Send a request to GPT
    params = {
        "model": "gpt-4o",
        "messages": prompt_messages,
        "temperature": 0,
        #"n":0.5,  
        "max_tokens": 4096,
    }

    client = OpenAI(
    
    api_key=open_ai_key,
)

    with st.spinner('AI analyzing...'):
        result = client.chat.completions.create(**params)

        response = result.choices[0].message.content

        
        

        

        # Display the response in two expander boxes
        with st.expander("Commentary", expanded= True):
            st.write(response)
            

            
            


       




    

   

