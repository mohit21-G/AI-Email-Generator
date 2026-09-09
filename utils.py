import os
import cohere
from dotenv import load_dotenv

load_dotenv()


def _get_cohere_key():
    try:
        import streamlit as st
        if "COHERE_API_KEY" in st.secrets and st.secrets["COHERE_API_KEY"]:
            return str(st.secrets["COHERE_API_KEY"])
    except Exception:
        pass
    return os.getenv("COHERE_API_KEY")


def getLLMResponse(form_input, email_sender, email_recipient, email_style):
    # Using Cohere Chat API directly since Generate API was removed in Sept 2025
    client = cohere.ClientV2(api_key=_get_cohere_key())

    prompt = f"""Write an email with {email_style} style and includes topic: {form_input}.

Sender: {email_sender}
Recipient: {email_recipient}

Email Text:
"""

    response = client.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": prompt}],
    )

    result = response.message.content[0].text
    print(result)
    return result
