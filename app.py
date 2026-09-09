import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_config(key: str, default: str = "") -> str:
    try:
        if key in st.secrets and st.secrets[key]:
            return str(st.secrets[key])
    except Exception:
        pass
    val = os.getenv(key)
    return val if val else default

raw_api_url = get_config("API_URL", "https://ai-email-generator-api.onrender.com/api/v1").rstrip("/")
API_URL = raw_api_url if raw_api_url.endswith("/api/v1") else f"{raw_api_url}/api/v1"
API_KEY = get_config("API_KEY", "9fK-7xP2mQ8vL4nR6sT1yZ5cW0aB3dE7h")

st.set_page_config(
    page_title="Generate Emails",
    page_icon="📧",
    layout="centered",
    initial_sidebar_state="collapsed",
)
st.header("Generate Emails 📧")

form_input = st.text_area("Enter the email topic", height=275)

# Creating columns for the UI - To receive inputs from user
col1, col2, col3 = st.columns([10, 10, 5])
with col1:
    email_sender = st.text_input("Sender Name")
with col2:
    email_recipient = st.text_input("Recipient Name")
with col3:
    email_style = st.selectbox(
        "Writing Style",
        ("Formal", "Appreciating", "Not Satisfied", "Neutral"),
        index=0,
    )

submit = st.button("Generate")

# When 'Generate' button is clicked, call the REST API
if submit:
    if not form_input or not form_input.strip():
        st.error("Please enter an email topic.")
    elif not email_sender or not email_sender.strip():
        st.error("Please enter the sender name.")
    elif not email_recipient or not email_recipient.strip():
        st.error("Please enter the recipient name.")
    else:
        endpoint = f"{API_URL}/email/generate"
        headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
        payload = {
            "topic": form_input,
            "sender": email_sender,
            "recipient": email_recipient,
            "style": email_style,
        }

        with st.spinner("Generating email via REST API..."):
            try:
                res = requests.post(endpoint, json=payload, headers=headers, timeout=(10, 45))
                if res.status_code == 200:
                    data = res.json()
                    email_text = data.get("data", {}).get("email_text", "")
                    st.success("Email generated successfully!")
                    st.write(email_text)
                else:
                    try:
                        err_json = res.json()
                        err_msg = err_json.get("message", "API returned error status")
                        err_detail = err_json.get("error", {}).get("detail", res.text)
                    except Exception:
                        err_msg = res.reason
                        err_detail = res.text
                    st.error(f"API Error ({res.status_code}): {err_msg}")
                    st.caption(f"Details: {err_detail}")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as net_err:
                err_label = "timed out" if isinstance(net_err, requests.exceptions.Timeout) else "unreachable"
                st.warning(f"⚠️ FastAPI backend server {err_label} at {endpoint}")
                st.info("Falling back to local service execution...")
                try:
                    from utils import getLLMResponse

                    response = getLLMResponse(form_input, email_sender, email_recipient, email_style)
                    st.success("Email generated successfully!")
                    st.write(response)
                except Exception as ex:
                    st.error(f"Fallback generation failed: {str(ex)}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
