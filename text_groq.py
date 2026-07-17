
from groq import Groq
import streamlit as st

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

reply = client.models.generate_content(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)
print(reply.choices[0].message)