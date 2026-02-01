import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Setup - Replace with your key or use st.secrets for security
# Get your key at: https://aistudio.google.com/
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Sales Engine Prototype", layout="wide")

# UI Header
st.title("🚀 Sales Sidekick AI")
st.subheader("Chat with your sales docs, support logs, and API guides.")

# Sidebar for file uploads
with st.sidebar:
    st.header("Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload Sales Material (PDFs)", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Helper function to extract text from PDFs
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# The Chat Logic
if prompt := st.chat_input("Ask a question about our products..."):
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare the context from uploaded files
    context = ""
    if uploaded_files:
        with st.spinner("Analyzing documents..."):
            context = get_pdf_text(uploaded_files)

    # Generate Response
    with st.chat_message("assistant"):
        try:
           model = genai.GenerativeModel("gemini-3-flash-preview")
            
            # This is the "Magic" prompt that tells the AI how to behave
           full_prompt = f"""
           You are a Sales Enablement Assistant. Use the following context to answer the question.
           If the answer isn't in the context, say you don't know based on current docs.
            
            Context: {context}
            User Question: {prompt}
            """
            
           response = model.generate_content(full_prompt)
           st.markdown(response.text)
           st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
