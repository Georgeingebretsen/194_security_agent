import streamlit as st
import pandas as pd
from security_checker import check_code_security
import io

st.set_page_config(layout="wide")

st.title("🤖 AI Code Security Checker")
st.write("Upload a code file and enter your OpenAI API key to get a basic security analysis.")

# --- Inputs ---
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Choose a code file", type=None) # Allow any file type for now

with col2:
    api_key = st.text_input("OpenAI API Key", type="password", help="Your API key is used to call the OpenAI API.")

analyze_button = st.button("Analyze Code")

# --- Analysis and Output ---
st.divider()

if analyze_button:
    if uploaded_file is not None and api_key:
        # To pass the file content to check_code_security, we need to read it
        # Since check_code_security expects a file path, we'll read the content 
        # and modify check_code_security to accept content directly.
        # (Alternative: save uploaded file temporarily, pass path - more complex)
        
        # Read file content
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        code_content = stringio.read()

        # We need to modify check_code_security to accept content instead of path
        # Let's assume we'll do that next.
        st.info(f"Analyzing code from: {uploaded_file.name}...")
        with st.spinner('Waiting for AI analysis...'):
             # Call the updated check_code_security with the file content
             result = check_code_security(code_content, api_key)

        st.subheader("Analysis Results")
        if isinstance(result, str) and result.startswith("Error:"):
            st.error(result)
        elif isinstance(result, list):
            if not result:
                st.success("No issues found.")
            else:
                # Simple display for now, filtering happens in check_code_security
                df = pd.DataFrame(result)
                # Reorder and rename columns for better display
                df_display = df.rename(columns={'line': 'Line', 'severity': 'Severity', 'issue': 'Issue'})
                if 'Line' in df_display.columns:
                     df_display = df_display[['Line', 'Severity', 'Issue']]
                st.dataframe(df_display, use_container_width=True)
        else:
            st.warning("Received unexpected result format:")
            st.write(result)
            
    elif not uploaded_file:
        st.warning("Please upload a code file.")
    else:
        st.warning("Please enter your OpenAI API key.") 