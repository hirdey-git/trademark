import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import requests

# Load environment variables (useful if you test locally with .env)
load_dotenv()

# Load API keys from Streamlit Secrets
openai_api_key = st.secrets["openai"]["api_key"]
rapidapi_key = st.secrets["rapidapi"]["key"]

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Streamlit UI
st.title("📝 Trademark Risk Checker")

# User inputs
trademark_text = st.text_input("Enter a phrase to check for trademark issues (e.g., 'Pink Elephant'):")
industry = st.text_input("Enter your industry (e.g., beverages, tech, clothing):")

# Function to check trademark via RapidAPI
def check_rapidapi_trademark(keyword):
    url = f"https://uspto-trademark.p.rapidapi.com/v1/trademarkSearch/{keyword}/all"
    headers = {
        "x-rapidapi-host": "uspto-trademark.p.rapidapi.com",
        "x-rapidapi-key": rapidapi_key
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        items = response.json().get("items", [])
        return len(items) > 0
    except Exception:
        return False

# When button is clicked
if st.button("Check Trademark Risk"):
    if not trademark_text or not industry:
        st.warning("Please fill out both fields.")
    else:
        # Check via RapidAPI
        found_in_rapidapi = check_rapidapi_trademark(trademark_text)

        # Construct prompt
        prompt = f"""
You are a legal and business research assistant with deep knowledge of public trademark databases (like USPTO, EUIPO, WIPO), and access to RapidAPI's USPTO Trademark API.

Step 1: You searched for "{trademark_text}" using the RapidAPI trademark database.

Step 2: {"You found matching results." if found_in_rapidapi else "No results were found via RapidAPI, so you're falling back to simulated research based on public data up to 2024."}

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
- A “Resources Used” section listing typical public sources this analysis is based on (e.g., {"RapidAPI USPTO Trademark API" if found_in_rapidapi else "USPTO TSDR, EUIPO TMView, WIPO Madrid Monitor, etc."})

Be concise, factual, and clearly structured in sections.
"""

        try:
            with st.spinner("Analyzing..."):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a trademark and business research assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                result = response.choices[0].message.content
                st.success("Trademark analysis complete:")
                st.markdown(result)
        except Exception as e:
            st.error(f"❌ Error from OpenAI API: {str(e)}")
