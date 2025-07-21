import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

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
exact_match = st.checkbox("Use exact match (quoted search)?", value=True)

# Function to check USPTO trademarks via RapidAPI
def check_rapidapi_trademark(keyword, use_quotes=True):
    search_term = f'"{keyword}"' if use_quotes else keyword
    url = f"https://uspto-trademark.p.rapidapi.com/v1/trademarkSearch/{search_term}/all"
    headers = {
        "x-rapidapi-host": "uspto-trademark.p.rapidapi.com",
        "x-rapidapi-key": rapidapi_key
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        items = response.json().get("items", [])
        return items
    except Exception:
        return []

# Function to simulate Common Law mentions using DuckDuckGo HTML scraping
def fetch_common_law_mentions(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        duck_url = f"https://html.duckduckgo.com/html?q={query}"
        resp = requests.get(duck_url, headers=headers, timeout=10)
        results = []
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for r in soup.select(".result__a")[:5]:
                href = r.get("href", "")
                title = r.get_text(strip=True)
                results.append((title, href))
        return results
    except Exception:
        return []

# On button click
if st.button("Check Trademark Risk"):
    if not trademark_text or not industry:
        st.warning("Please fill out both fields.")
    else:
        # 1. USPTO trademark check
        trademark_results = check_rapidapi_trademark(trademark_text, exact_match)
        found_in_rapidapi = len(trademark_results) > 0

        # 2. Common Law web mentions
        common_law_hits = fetch_common_law_mentions(trademark_text)
        common_law_section = "\n".join(
            [f"{i+1}. **{title}** – [Link]({link})" for i, (title, link) in enumerate(common_law_hits)]
        ) or "No notable common law hits found."

        # 3. Generate prompt
        prompt = f"""
You are a legal and business research assistant with access to public trademark databases (USPTO, EUIPO, WIPO) and general web presence awareness.

Step 1: You searched for "{trademark_text}" using the USPTO RapidAPI trademark database.
Step 2: {"Trademark(s) were found." if found_in_rapidapi else "No exact matches found in the trademark registry."}

You also checked common law usage by reviewing general web presence for the phrase.

Given the phrase: "{trademark_text}"

Provide a summary including:
1. Whether it's registered or known as a trademark.
2. Associated goods/services.
3. Likely owner(s), jurisdictions, and class codes.
4. If it is active, pending, or abandoned.
5. Common law conflicts from existing businesses, domains, or media uses.

**Common Law Mentions:**  
{common_law_section}

Conclude with:
- A risk rating for using “{trademark_text}” in the {industry} industry (low, medium, high)
- Disclaimer that this is a simulated summary, not legal advice.
- List resources used.
"""

        # 4. Call OpenAI
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
