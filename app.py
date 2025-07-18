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
You are a legal and business research assistant with deep knowledge of public trademark databases (like USPTO, EUIPO, WIPO), but you cannot directly access them in real-time.

Instead, use your training data, publicly known trademarks up to 2024, and reasonable inferences to simulate a trademark research summary.

Given the phrase: "{trademark_text}"

Provide a well-structured summary that includes:

1. Whether "{trademark_text}" is known as a registered or commonly used trademark.
2. What types of goods or services it is associated with (e.g., software, beverages, clothing).
3. Any known or likely owner(s) of the mark.
4. Common jurisdictions it might be registered in (e.g., US, EU).
5. Relevant trademark classes (e.g., Class 32 for beverages).
6. Whether it is likely active, pending, or abandoned.
7. Any potential risks of using a similar name in the {industry} industry.

Conclude with:
- A plain-English risk rating for using “{trademark_text}” in the {industry} industry (low, medium, high)
- A short disclaimer stating that this is a simulated estimate, not legal advice
- A “Resources Used” section listing typical public sources this analysis is based on (e.g., USPTO TSDR, EUIPO TMView, WIPO Madrid Monitor, trademark classification standards, etc.)

Be concise, factual, and clearly structured in sections.
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
