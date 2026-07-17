import streamlit as st
from groq import Groq
import pandas as pd
from app_model.cyber_incidents import get_all_cyber_incidents
from app_model.it_tickets import get_all_it_tickets
from app_model.metadata import get_all_datasets_metadata
from app_model.db import get_connection

#authenticator checker

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.error("Please log in to access the chatbot.")
    st.stop()


#API key 
client = Groq(api_key=st.secrets["GROQ_API_KEY"])


#loading data from the database
@st.cache_data#we use cache so it only runs once per session
def load_data():
    conn = get_connection()
    cyber   = get_all_cyber_incidents(conn)
    tickets = get_all_it_tickets(conn)
    meta    = get_all_datasets_metadata(conn)
    conn.close()
    return cyber, tickets, meta

cyber_data, ticket_data, meta_data = load_data()

#specific prompts for each domain
DOMAINS = {
    "General Assistant": """
You are an AI assistant for a company's internal dashboard.
You MUST ONLY answer questions that relate to cyber incidents, IT support tickets,
dataset metadata, or information contained in the company database.
If a user asks about anything else, respond exactly:
"I'm only able to answer questions related to the company's database and dashboard."
Never use outside knowledge. Never guess. Only use the database information provided.
""",

    "Cyber Security Analyst": """
You are a senior cyber security analyst embedded in a company's security dashboard.
Help analysts understand incidents, identify threat patterns, and recommend remediation.
Rules:
1. Assess severity before recommending actions.
2. Recommend containment FIRST, then investigation, then remediation.
3. If data is incomplete, state what additional information is needed.
4. Never speculate beyond the data — flag uncertainty clearly.
5. Use structured output: Cause / Impact / Recommended Actions.
""",

    "IT Support Agent": """
You are a senior IT support agent embedded in a company help desk dashboard.
Help technicians diagnose and resolve IT tickets efficiently.
Rules:
1. Start from the simplest likely cause before escalating.
2. Suggest specific, actionable troubleshooting steps in numbered order.
3. Flag escalation for high priority or long-unresolved tickets.
4. State clearly if on-site intervention is needed.
5. Never promise resolution timelines you cannot guarantee.
6. Use structured output: Likely Cause / Steps / Escalation Flag.
""",
}



def ticket_context() -> str:
    t = ticket_data

    #computing all counts in python
    total        = len(t)
    open_t       = t[t["status"] != "Closed"]
    closed_t     = t[t["status"] == "Closed"]
    in_progress  = t[t["status"] == "In Progress"] 
    high_p       = t[t["priority"] == "High"]      
    open_high    = open_t[open_t["priority"] == "High"] 

    sample_cols = [c for c in ["ticket_id", "priority", "status", "description"] if c in t.columns]

    return f"""
TICKET COUNTS (calculated directly from the database — treat these as ground truth):
  Total tickets      : {total}
  Open tickets       : {len(open_t)}
  Closed tickets     : {len(closed_t)}
  In Progress        : {len(in_progress)}
  High priority      : {len(high_p)}
  Open + High priority: {len(open_high)}

Priority breakdown (all tickets):
{t["priority"].value_counts().to_string()}

Status breakdown (all tickets):
{t["status"].value_counts().to_string()}

Sample open tickets (up to 10):
{open_t[sample_cols].head(10).to_string(index=False)}
""".strip()


def incident_context() -> str:
    c = cyber_data

    total        = len(c)
    open_c       = c[c["status"] != "Closed"]
    closed_c     = c[c["status"] == "Closed"]
    critical     = c[c["severity"] == "Critical"] 
    open_critical = open_c[open_c["severity"] == "Critical"] 

    sample_cols = [col for col in ["incident_id", "severity", "category", "status"] if col in c.columns]

    return f"""
INCIDENT COUNTS (calculated directly from the database — treat these as ground truth):
  Total incidents        : {total}
  Open incidents         : {len(open_c)}
  Closed incidents       : {len(closed_c)}
  Critical severity      : {len(critical)}
  Open + Critical        : {len(open_critical)}

Severity breakdown (all incidents):
{c["severity"].value_counts().to_string()}

Category breakdown (all incidents):
{c["category"].value_counts().to_string()}

Status breakdown (all incidents):
{c["status"].value_counts().to_string()}

Sample open incidents (up to 10):
{open_c[sample_cols].head(10).to_string(index=False)}
""".strip()


def metadata_context() -> str:
    cols = [c for c in ["dataset_id", "name", "rows", "columns", "uploaded_by", "upload_date"] if c in meta_data.columns]
    return f"""
DATASET METADATA (calculated directly from the database — treat these as ground truth):
  Total datasets: {len(meta_data)}

Full list:
{meta_data[cols].to_string(index=False)}
""".strip()


#keywords the API should look out for when ansering questions related to the database

TICKET_KEYWORDS = {
    "ticket", "tickets", "it ticket", "it tickets", "helpdesk", "help desk",
    "support ticket", "support tickets", "open ticket", "closed ticket",
    "it support", "it issue", "it issues", "it request",
}

INCIDENT_KEYWORDS = {
    "incident", "incidents", "cyber incident", "cyber incidents",
    "cyber attack", "cyber attacks", "security incident", "security incidents",
    "breach", "breaches", "attack", "attacks", "threat", "threats",
    "malware", "phishing", "ransomware", "vulnerability", "vulnerabilities",
}

METADATA_KEYWORDS = {
    "metadata", "dataset", "datasets", "data set", "data sets",
    "upload", "uploads", "uploaded", "file", "files",
}

def database_context(question: str) -> str:
    question = question.lower()

    is_ticket   = any(word in question for word in TICKET_KEYWORDS)
    is_incident = any(word in question for word in INCIDENT_KEYWORDS)
    is_metadata = any(word in question for word in METADATA_KEYWORDS)

    if is_incident and is_ticket:
        inc_hits = sum(word in question for word in INCIDENT_KEYWORDS)
        tkt_hits = sum(word in question for word in TICKET_KEYWORDS)
        is_incident = inc_hits >= tkt_hits
        is_ticket   = not is_incident

    if is_ticket:
        return ticket_context()
    if is_incident:
        return incident_context()
    if is_metadata:
        return metadata_context()
    return ""


#streaming function so the API doesn't paste the full response at once
def stream_groq(messages: list[dict]) -> str:
    response = ""
    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            stream = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                text = chunk.choices[0].delta.content or ""
                if text:
                    response += text
                    placeholder.markdown(response)
        except Exception as e:
            st.error(f"Groq Error: {e}")
            response = "Unable to generate a response."
    st.session_state.messages.append({"role": "assistant", "content": response})
    return response


#user interface
st.title("💬 Chat with Groq")

domain = st.selectbox("Choose Assistant", list(DOMAINS.keys()))
system_prompt = DOMAINS[domain]
st.caption(f"Current Assistant: **{domain}**")

if st.session_state.get("current_domain") != domain:
    st.session_state.messages = []
    st.session_state.current_domain = domain

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Chat Options")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask a question about the database...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Fetching data…"):
        db_context = database_context(prompt)

    system_content = system_prompt.strip()
    if db_context:
        system_content += f"""

VERIFIED DATABASE RECORDS — these numbers were computed directly in Python.
You MUST use exactly these figures in your answer. Do NOT recalculate or estimate.

{db_context}
"""

    messages = [{"role": "system", "content": system_content}]
    messages += [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    stream_groq(messages)