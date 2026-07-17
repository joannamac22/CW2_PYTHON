import streamlit as st
import pandas as pd
from app_model.cyber_incidents import get_all_cyber_incidents
from app_model.it_tickets import get_all_it_tickets
from app_model.metadata import get_all_datasets_metadata
from app_model.db import get_connection
from app_model.users import get_all_users

st.set_page_config(
    page_title="Dashboard",
    page_icon="🛡️",
    layout="wide"
)

#authentication check
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.error("Please log in to access the dashboard.")
    st.stop()

#Load all data from a single connection
conn = get_connection()

cyber_data = get_all_cyber_incidents(conn)
ticket_data = get_all_it_tickets(conn)
meta_data = get_all_datasets_metadata(conn)
all_users = get_all_users(conn)

conn.close()

cyber_data["timestamp"] = pd.to_datetime(cyber_data["timestamp"])
ticket_data["created_at"] = pd.to_datetime(ticket_data["created_at"])

#page title
st.title("🛡️ Security Operations Dashboard")
st.markdown("---")

#summary metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Incidents", len(cyber_data))
with col2:
    severity_incidents = len(cyber_data[cyber_data["severity"] == "Medium"])
    st.metric("Medium Severity Incidents", severity_incidents)
with col3:
    open_tickets = len(ticket_data[ticket_data["status"] == "Open"])
    st.metric("Open IT Tickets", open_tickets)
with col4:
    avg_resolution = round(ticket_data["resolution_time_hours"].mean(), 1)
    st.metric("Avg Resolution (hrs)", avg_resolution)

st.markdown("---")

#Build tab list
tab_labels = ["🔒 Cyber Incidents", "🎫 IT Tickets", "📂 Datasets"]

tabs = st.tabs(tab_labels)

tab1 = tabs[0]
tab2 = tabs[1]
tab3 = tabs[2]

#CYBER INCIDENTS
with tab1:
    st.subheader("Cyber Incidents")

    with st.sidebar:
        st.header("Filters")
        severity_filter = st.selectbox("Severity", ["All"] + list(cyber_data["severity"].unique()))
        status_filter = st.selectbox("Status", ["All"] + list(cyber_data["status"].unique()))

    filtered_cyber = cyber_data.copy()
    if severity_filter != "All":
        filtered_cyber = filtered_cyber[filtered_cyber["severity"] == severity_filter]
    if status_filter != "All":
        filtered_cyber = filtered_cyber[filtered_cyber["status"] == status_filter]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Incidents by Category**")
        st.bar_chart(filtered_cyber["category"].value_counts())
    with col2:
        st.markdown("**Incidents by Severity**")
        st.bar_chart(filtered_cyber["severity"].value_counts())

    st.markdown("**Incidents Over Time**")
    trend = filtered_cyber.set_index("timestamp").resample("ME").size()
    st.line_chart(trend)

    st.markdown("**Incident Records**")
    st.dataframe(filtered_cyber, width="stretch")



#IT TICKETS
with tab2:
    st.subheader("IT Tickets")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Tickets by Priority**")
        st.bar_chart(ticket_data["priority"].value_counts())
    with col2:
        st.markdown("**Tickets by Status**")
        st.bar_chart(ticket_data["status"].value_counts())

    st.markdown("**Average Resolution Time by Priority (hours)**")
    avg_by_priority = ticket_data.groupby("priority")["resolution_time_hours"].mean().round(1)
    st.bar_chart(avg_by_priority)

    st.markdown("**Ticket Records**")
    st.dataframe(ticket_data, width="stretch")


#DATASETS
with tab3:
    st.subheader("Datasets Overview")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Dataset Sizes (rows)**")
        st.bar_chart(meta_data.set_index("name")["rows"])
    with col2:
        st.markdown("**Uploads by User**")
        st.bar_chart(meta_data["uploaded_by"].value_counts())

    st.markdown("**All Datasets**")
    st.dataframe(meta_data, width="stretch")


