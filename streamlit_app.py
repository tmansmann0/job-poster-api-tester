
import streamlit as st
import requests
import json

st.set_page_config(page_title="Job Poster API Tester")

# Initialize modules state
if 'modules' not in st.session_state:
    st.session_state.modules = None

st.title("Job Poster API Tester")

# Sidebar for API base URL
base_url = st.sidebar.text_input("API Base URL", "https://job-poster-r0c5.onrender.com")

# Fetch modules
if st.sidebar.button("Fetch Modules"):
    try:
        resp = requests.get(base_url.rstrip("/") + "/api/modules")
        resp.raise_for_status()
        data = resp.json()
        st.session_state.modules = data.get("modules", [])
        st.sidebar.success("Fetched modules")
    except Exception as e:
        st.sidebar.error(f"Error fetching modules: {e}")

# Display modules in sidebar if loaded
if st.session_state.modules:
    st.sidebar.subheader("Available Modules")
    for mod in st.session_state.modules:
        st.sidebar.write(f"{mod['id']}: {mod.get('label', '')}")

st.header("Submit a Job")

# Job URL
job_url = st.text_input("Job URL (optional)")

# Fields JSON input
fields_input = st.text_area(
    "Job fields JSON (optional)",
    placeholder='{"title": "My Job", "hiringOrganization": {"name": "My Company"}, "descriptionHTML": "<p>Job description here</p>"}'
)

# Credentials JSON input
creds_input = st.text_area(
    "Per-request credentials JSON (optional)",
    placeholder='{"indeed": {"clientId": "", "clientSecret": ""}, "google": {"serviceAccountJson": ""}}'
)

# Module selection
module_options = [mod['id'] for mod in st.session_state.modules] if st.session_state.modules else []
selected_modules = st.multiselect("Publish to modules", module_options)

# Hold if incomplete
hold_if_incomplete = st.checkbox("Hold if incomplete", value=True)

# Submit button
if st.button("Submit Job"):
    payload = {}
    if job_url:
        payload["url"] = job_url
    # parse fields JSON
    if fields_input.strip():
        try:
            payload["fields"] = json.loads(fields_input)
        except Exception as e:
            st.error(f"Invalid fields JSON: {e}")
    # parse creds JSON
    if creds_input.strip():
        try:
            payload["credentials"] = json.loads(creds_input)
        except Exception as e:
            st.error(f"Invalid credentials JSON: {e}")
    # modules selection
    if selected_modules:
        payload["modules"] = selected_modules
    else:
        payload["modules"] = "all"
    payload["holdIfIncomplete"] = hold_if_incomplete

    # Send POST request
    try:
        res = requests.post(base_url.rstrip("/") + "/api/jobs", json=payload)
        st.write(f"Status code: {res.status_code}")
        try:
            st.json(res.json())
        except Exception:
            st.write(res.text)
    except Exception as e:
        st.error(f"Error submitting job: {e}")
