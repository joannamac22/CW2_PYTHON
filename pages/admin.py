import streamlit as st
from app_model.db import get_connection
from app_model.users import get_all_users, add_user, delete_user, update_user_role
from app_model.admin_data import add_it_ticket, add_cyber_incident, add_dataset_metadata
from  hashing import hash_password

# Authentication check for admin only 
if not st.session_state.get("logged_in"):
    st.error("Please log in to access this page.")
    st.stop()

if st.session_state.get("role") != "admin":
    st.error("⛔ Access denied. Admins only.")
    st.stop()

st.title("🛠️ Admin Panel")

conn = get_connection()

#TABS
tab_users, tab_tickets, tab_incidents, tab_metadata = st.tabs([
    "👥 Users",
    "🎫 IT Tickets",
    "🔐 Cyber Incidents",
    "🗄️ Dataset Metadata",
])

#USER MANAGEMENT
with tab_users:
    st.subheader("Existing Users")

    users = get_all_users(conn)

    if not users:
        st.info("No users found.")
    else:
        for user in users:
            col_name, col_role, col_change, col_delete = st.columns([3, 2, 2, 1])

            with col_name:
                st.write(f"**{user['username']}**")

            with col_role:
                st.write(f"`{user['role']}`")

            with col_change:
                new_role = st.selectbox(
                    "Change role",
                    options=["user", "admin"],
                    index=0 if user["role"] == "user" else 1,
                    key=f"role_{user['username']}",
                    label_visibility="collapsed",
                )
                if new_role != user["role"]:
                    if st.button("Save", key=f"save_{user['username']}"):
                        ok, msg = update_user_role(conn, user["username"], new_role)
                        st.success(msg) if ok else st.error(msg)
                        st.rerun()

            with col_delete:
                if st.button("🗑️", key=f"del_{user['username']}", help="Delete user"):
                    current_username = st.session_state.get("username")
                    ok, msg = delete_user(conn, user["username"], current_username)
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()

    st.divider()
    st.subheader("Add New User")

    with st.form("add_user_form", clear_on_submit=True):
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", ["user", "admin"])
        submitted = st.form_submit_button("➕ Create User")

        if submitted:
            if not new_username.strip():
                st.error("Username cannot be empty.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                hashed = hash_password(new_password)
                ok, msg = add_user(conn, new_username, new_role, hashed)
                st.success(msg) if ok else st.error(msg)
                if ok:
                    st.rerun()


#IT TICKETS
with tab_tickets:
    st.subheader("Add IT Ticket")

    with st.form("add_ticket_form", clear_on_submit=True):
        t_title = st.text_input("Title")
        t_description = st.text_area("Description")
        t_col1, t_col2 = st.columns(2)
        t_priority = t_col1.selectbox("Priority", ["Low", "Medium", "High"])
        t_severity = t_col2.selectbox("Severity", ["Low", "Medium", "High"])
        t_assigned = st.text_input("Assigned To (optional)")
        t_submitted = st.form_submit_button("➕ Add Ticket")

        if t_submitted:
            ok, msg = add_it_ticket(conn, t_title, t_description, t_priority, t_severity, t_assigned)
            st.success(msg) if ok else st.error(msg)


#CYBER INCIDENTS
with tab_incidents:
    st.subheader("Add Cyber Incident")

    INCIDENT_CATEGORIES = [
        "Phishing", "Ransomware", "Data Breach", "Malware",
        "Unauthorised Access", "DDoS", "Insider Threat", "Other",
    ]

    with st.form("add_incident_form", clear_on_submit=True):
        i_title = st.text_input("Title")
        i_desc = st.text_area("Description")
        i_col1, i_col2 = st.columns(2)
        i_severity = i_col1.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        i_category = i_col2.selectbox("Category", INCIDENT_CATEGORIES)
        i_systems = st.text_input("Affected Systems (optional)")
        i_submitted = st.form_submit_button("➕ Add Incident")

        if i_submitted:
            ok, msg = add_cyber_incident(conn, i_title, i_desc, i_severity, i_category, i_systems)
            st.success(msg) if ok else st.error(msg)


#DATASET METADATA
with tab_metadata:
    st.subheader("Add Dataset Metadata")

    with st.form("add_metadata_form", clear_on_submit=True):
        m_name = st.text_input("Dataset Name")
        m_col1, m_col2 = st.columns(2)
        m_rows = m_col1.number_input("Rows", min_value=0, step=1)
        m_columns = m_col2.number_input("Columns", min_value=0, step=1)
        m_uploader = st.text_input("Uploaded By")
        m_desc = st.text_area("Description (optional)")
        m_submitted = st.form_submit_button("➕ Add Dataset")

        if m_submitted:
            ok, msg = add_dataset_metadata(conn, m_name, int(m_rows), int(m_columns), m_uploader, m_desc)
            st.success(msg) if ok else st.error(msg)

conn.close()