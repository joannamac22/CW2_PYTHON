# Installation

## 1. Clone the repository

git clone <repository-url>
or download the ZIP file and extract it.

## 2. Open the project

Open the project folder using Visual Studio Code.


## 3. Create a virtual environment (optional but recommended)

Windows
python -m venv .venv

Activate it
.venv\Scripts\activate

## 4. Install dependencies

pip install -r requirements.txt

If a requirements file is not included:
pip install streamlit pandas bcrypt groq

## 5. Configure the API key

Create the following file if it does not already exist:
.streamlit/secrets.toml

Add your Groq API key:
GROQ_API_KEY = "YOUR_API_KEY"

## 6. Run the application

streamlit run home.py
or
python -m streamlit run home.py
The application will automatically open in your browser.

# Logging in as a User

1. Open the login page.
2. Enter your username.
3. Enter your password.
4. Click **Login**.
5. After successful authentication you will be redirected to the dashboard.

A standard user can:

- View Cybersecurity Incidents
- View IT Tickets
- View Dataset Metadata
- Use the AI Assistant
- Navigate between dashboards

Users cannot perform administrative tasks.

# Logging in as an Administrator

1. Open the login page.
2. Enter an administrator username(Joanna)
3. Enter the administrator password(Joanna123456)
4. Click **Login**.

The administrator has full access to the platform.

Administrator features include:

- Add users
- Delete users
- Add Cybersecurity Incidents
- Add IT Tickets
- Manage the database through the dashboard
- View all dashboards
- Use the AI Assistant

# AI Assistant

The platform contains three AI domains.

### General Assistant

Answers only questions related to the company's database.

### Cyber Security Analyst

- Explains cybersecurity incidents
- Assesses severity
- Suggests mitigation steps
- Assists with investigations

### IT Support Agent

- Analyses IT tickets
- Suggests troubleshooting steps
- Identifies likely causes
- Provides escalation guidance


# Troubleshooting

## Streamlit not recognised

Run:
python -m streamlit run home.py

or install Streamlit:

pip install streamlit

## API Key Error

Ensure the following file exists:
.streamlit/secrets.toml

and contains:

```toml
GROQ_API_KEY="YOUR_API_KEY"


## Database Errors

Ensure:

- `database.db` exists.
- The SQLite tables have been created.
- The database path is correct in `db.py`.
