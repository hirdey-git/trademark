import streamlit as st
from scraper import search_trademark_tess
from utils import summarize_confidence

st.set_page_config(page_title="USPTO Trademark Search AI", layout="centered")

st.title("🔍 AI-Powered Trademark Search Tool")
st.markdown("Search the USPTO database for existing or similar trademarks using AI.")

query = st.text_input("Enter your desired word mark", placeholder="e.g., Let’s do it")
industry = st.text_input("Enter relevant industry or classification", placeholder="e.g., clothing, food, software")

if st.button("Search"):
    if not query.strip() or not industry.strip():
        st.warning("Please enter both word mark and industry.")
    else:
        with st.spinner("Searching USPTO..."):
            results = search_trademark_tess(query)
            if not results:
                st.info("No similar trademarks found.")
            else:
                st.success(f"Found {len(results)} similar trademarks.")
                st.subheader("📄 Raw Results:")
                for res in results:
                    st.markdown(f"- {res}")

                st.subheader("🧠 AI Summary & Confidence Level")
                summary = summarize_confidence(query, industry, results)
                st.markdown(summary)