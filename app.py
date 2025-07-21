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
        citation_links = "\n".join(
            [f"{i+1}. [{title}]({link})" for i, (title, link) in enumerate(common_law_hits)]
        ) or "No common law citations found."

        common_law_note = (
            "### Common Law Mentions (from public web search)\n\n"
            "Below are real-world citations gathered from DuckDuckGo that may indicate existing common law usage of the phrase:\n\n"
            f"{citation_links}\n\n"
        )

        # 3. Generate prompt
        prompt = f"""
You are a legal and business research assistant with access to public trademark databases (USPTO, EUIPO, WIPO) and awareness of publicly available web information.

Step 1: You searched for "{trademark_text}" using the USPTO RapidAPI trademark database.
Step 2: {"Trademark(s) were found." if found_in_rapidapi else "No exact matches found in the trademark registry."}

You also checked common law usage through general web search results.

Given the phrase: "{trademark_text}"

Provide a summary that includes:
1. Whether it is known as a registered or commonly used trademark.
2. What goods or services it's associated with.
3. Known or likely owner(s).
4. Jurisdictions and trademark classes.
5. Whether it is active, pending, or abandoned.
6. Any common law risk based on other businesses, domains, or public use.

{common_law_note}

Conclude with:
- A risk rating (low, medium, high) for using “{trademark_text}” in the {industry} industry
- Disclaimer that this is a simulated summary, not legal advice
- Resources used (including USPTO and citation links above)
"""

        # 4. Call OpenAI
        try:
            with st.spinner("Analyzing..."):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a trademark and business research assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )
                result = response.choices[0].message.content
                st.success("Trademark analysis complete:")
                st.markdown(result)
        except Exception as e:
            st.error(f"❌ Error from OpenAI API: {str(e)}")
