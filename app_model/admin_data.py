
#Admin-only database that provides functions for IT tickets, cyber incidents, and dataset metadata.

from datetime import datetime

#IT tickets
def add_it_ticket(
    conn,
    title: str,
    description: str,
    priority: str,
    severity: str,
    assigned_to: str = "",) -> tuple[bool, str]:
    if not title.strip():
        return False, "Title cannot be empty."
    if priority not in ("Low", "Medium", "High"):
        return False, "Priority must be Low, Medium, or High."
    if severity not in ("Low", "Medium", "High"):
        return False, "Severity must be Low, Medium, or High."

    try:
        conn.execute(
            """
            INSERT INTO it_tickets (title, description, priority, severity, status, assigned_to, created_at)
            VALUES (?, ?, ?, ?, 'Open', ?, ?)
            """,
            (title.strip(), description.strip(), priority, severity, assigned_to.strip(), datetime.utcnow()),)
        conn.commit()
        return True, f"Ticket '{title}' created successfully."
    except Exception as e:
        return False, f"Database error: {e}"


#Cyber incidents
def add_cyber_incident(
    conn,
    title: str,
    description: str,
    severity: str,
    category: str,
    affected_systems: str = "",) -> tuple[bool, str]:
    if not title.strip():
        return False, "Title cannot be empty."
    if severity not in ("Low", "Medium", "High", "Critical"):
        return False, "Severity must be low, medium, high, or critical."
    if not category.strip():
        return False, "Category cannot be empty."

    try:
        conn.execute(
            """
            INSERT INTO cyber_incidents (title, description, severity, category, status, affected_systems, created_at)
            VALUES (?, ?, ?, ?, 'Open', ?, ?)
            """,
            (title.strip(), description.strip(), severity, category.strip(), affected_systems.strip(), datetime.utcnow()),)
        conn.commit()
        return True, f"Incident '{title}' created successfully."
    except Exception as e:
        return False, f"Database error: {e}"


#Dataset metadata
def add_dataset_metadata(
    conn,
    name: str,
    rows: int,
    columns: int,
    uploaded_by: str,
    description: str = "",) -> tuple[bool, str]:
    if not name.strip():
        return False, "Dataset name cannot be empty."
    if rows < 0 or columns < 0:
        return False, "Rows and columns must not be negative."
    if not uploaded_by.strip():
        return False, "Uploaded by cannot be empty."

    try:
        conn.execute(
            """
            INSERT INTO datasets_metadata (name, rows, columns, uploaded_by, description, upload_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name.strip(), rows, columns, uploaded_by.strip(), description.strip(), datetime.utcnow()),)
        conn.commit()
        return True, f"Dataset '{name}' added successfully."
    except Exception as e:
        return False, f"Database error: {e}"