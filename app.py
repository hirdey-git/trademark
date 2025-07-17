import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI



# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("📝 Trademark Risk Checker")

# User Inputs
trademark_text = st.text_input("Enter a phrase to check for trademark issues (e.g., 'Pink Elephant'):")
industry = st.text_input("Enter your industry (e.g., beverages, tech, clothing):")

# Button to run
if st.button("Check Trademark Risk"):
    if not trademark_text or not industry:
        st.warning("Please fill out both fields.")
    else:
        # Format prompt
        prompt = f"""
You are a legal and business research assistant with deep knowledge of public trademark databases, including the USPTO, EUIPO, and WIPO records up to 2024.

Given the phrase: "{trademark_text}"

Your task is to determine if this phrase is registered as a trademark or commonly used as a brand or product name. Provide a detailed summary that includes:

1. Whether "{trademark_text}" is a registered or known trademark.
2. The types of goods/services it is associated with (e.g., beer, clothing, software).
3. Who owns the trademark (e.g., company, individual).
4. Any known jurisdictions where it is registered (e.g., US, EU, Canada).
5. The relevant trademark classes (e.g., Class 32 for beverages).
6. Whether it is active, abandoned, or pending.
7. Any public legal or commercial risks involved in using a similar name.

Conclude with a plain-English risk assessment for using “{trademark_text}” as a brand name for a new business in the {industry} industry.

Respond in a structured and concise format.
"""

        # Call OpenAI
        try:
            with st.spinner("Checking..."):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a trademark and business research assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                result = response['choices'][0]['message']['content']
                st.success("Trademark analysis complete:")
                st.markdown(result)
        except Exception as e:
            st.error(f"Error contacting OpenAI API: {str(e)}")
