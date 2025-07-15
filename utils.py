import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_confidence(mark, industry, trademark_list):
    prompt = f"""
You are a legal trademark assistant. A user is trying to register the mark: "{mark}" in the industry: "{industry}".

Here are the top results from the USPTO for similar or matching trademarks:
{trademark_list}

Please analyze:
1. Whether any exact or confusingly similar marks exist.
2. Whether the existing trademarks are in a similar industry.
3. Risk/confidence of conflict (Low, Medium, High).
4. Brief justification for the confidence level.

Output should be clear and helpful for a business considering this mark.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an intelligent legal assistant specializing in trademark analysis."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=600
    )
    return response.choices[0].message.content