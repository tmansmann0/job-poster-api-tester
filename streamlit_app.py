import streamlit as st
import requests
import json
from typing import Dict, Any

st.set_page_config(page_title="Job Poster API Tester", page_icon="🧩", layout="wide")

# --- Helpers --------------------------------------------------------------
def fetch_modules(base_url: str):
    try:
        res = requests.get(f"{base_url.rstrip('/')}/api/modules", timeout=20)
        res.raise_for_status()
        return res.json().get("modules", [])
    except Exception as e:
        st.error(f"❌ Failed to fetch modules: {e}")
        return []

def post_json(base_url: str, payload: dict):
    try:
        res = requests.post(f"{base_url.rstrip('/')}/api/jobs", json=payload, timeout=60)
        try:
            return res.status_code, res.json()
        except Exception:
            return res.status_code, {"raw": res.text}
    except Exception as e:
        return 0, {"error": str(e)}

def clean_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    def _clean(v):
        if isinstance(v, dict):
            vv = {k: _clean(x) for k, x in v.items() if x not in ("", None)}
            return vv or None
        elif isinstance(v, list):
            ll = [_clean(x) for x in v if x not in ("", None)]
            return ll or None
        return v
    return {k: _clean(v) for k, v in d.items() if v not in ("", None)}

# --- Sidebar --------------------------------------------------------------
st.sidebar.title("⚙️ API Settings")
default_base = "https://job-poster-r0c5.onrender.com"
base_url = st.sidebar.text_input("API Base URL", default_base)
if st.sidebar.button("🔄 Refresh Modules"):
    st.session_state["modules"] = fetch_modules(base_url)

modules = st.session_state.get("modules")
if not modules:
    st.sidebar.info("Click 'Refresh Modules' to load module metadata.")
else:
    st.sidebar.success(f"Loaded {len(modules)} modules.")

# --- Main Interface -------------------------------------------------------
st.title("🧩 Job Poster API Tester — Form Builder")

tabs = st.tabs(["🧱 Form Builder", "🧾 Raw JSON Mode"])

# ===================================================
# 1️⃣ FORM BUILDER TAB
# ===================================================
with tabs[0]:
    st.header("Step 1: Job Details")

    url = st.text_input("Job URL (optional)")
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Job Title", "")
        employment = st.selectbox("Employment Type", ["", "FULL_TIME", "PART_TIME", "CONTRACT", "TEMPORARY", "INTERN", "VOLUNTEER", "PER_DIEM", "OTHER"])
        remote = st.selectbox("Remote Type", ["", "ONSITE", "REMOTE", "HYBRID"])
        date_posted = st.text_input("Date Posted (ISO)", "")
        valid_through = st.text_input("Valid Through (ISO)", "")
    with col2:
        apply_url = st.text_input("Apply URL", "")
        ref_id = st.text_input("Reference ID", "")
        app_loc_req = st.text_input("Applicant Location Requirements", "")

    st.subheader("Organization")
    org_col1, org_col2, org_col3 = st.columns(3)
    with org_col1:
        org_name = st.text_input("Org Name", "")
    with org_col2:
        org_site = st.text_input("Org Website", "")
    with org_col3:
        org_logo = st.text_input("Org Logo URL", "")

    st.subheader("Location (optional)")
    loc_col1, loc_col2, loc_col3, loc_col4 = st.columns(4)
    with loc_col1:
        addr_city = st.text_input("City")
    with loc_col2:
        addr_region = st.text_input("Region/State")
    with loc_col3:
        addr_postal = st.text_input("Postal Code")
    with loc_col4:
        addr_country = st.text_input("Country", "US")

    st.subheader("Salary (optional)")
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        sal_currency = st.text_input("Currency", "USD")
    with s_col2:
        sal_min = st.text_input("Min")
    with s_col3:
        sal_max = st.text_input("Max")
    with s_col4:
        sal_unit = st.selectbox("Unit", ["", "HOUR", "DAY", "WEEK", "MONTH", "YEAR"], index=4)

    st.subheader("Description (HTML)")
    description = st.text_area("Job Description", "<p>Enter a description...</p>", height=180)

    # Build job fields dict automatically
    job_fields = clean_dict({
        "title": title,
        "descriptionHTML": description,
        "hiringOrganization": {"name": org_name, "website": org_site, "logoUrl": org_logo},
        "employmentType": employment,
        "applyUrl": apply_url,
        "refId": ref_id,
        "remoteType": remote,
        "datePosted": date_posted,
        "validThrough": valid_through,
        "applicantLocationRequirements": app_loc_req,
        "addresses": [{
            "addressLocality": addr_city,
            "addressRegion": addr_region,
            "postalCode": addr_postal,
            "addressCountry": addr_country
        }],
        "salary": {
            "currency": sal_currency,
            "min": sal_min,
            "max": sal_max,
            "unit": sal_unit
        }
    })

    # --- Module chooser ---------------------------------------------------
    st.markdown("---")
    st.header("Step 2: Select Modules & Credentials")

    selected_ids = []
    if modules:
        for m in modules:
            with st.expander(f"📦 {m['label']} ({m['id']})"):
                st.markdown(f"**Required Fields:** {', '.join(m.get('requiredFields', [])) or '—'}")
                st.markdown(f"**Required Credentials:** {', '.join(m.get('requiredCredentials', [])) or '—'}")
                if st.checkbox(f"Enable {m['id']}", key=m['id']):
                    selected_ids.append(m['id'])
                if "indeed" in m['id']:
                    st.text_input(f"{m['id']} → Indeed Client ID", key=f"cid_{m['id']}")
                    st.text_input(f"{m['id']} → Indeed Client Secret", key=f"csec_{m['id']}", type="password")
                if "google" in m['id']:
                    st.text_area(f"{m['id']} → Google Service Account JSON", key=f"gsa_{m['id']}", height=100)
    else:
        st.info("No modules loaded yet. Use the sidebar to refresh.")

    st.markdown("---")
    st.header("Step 3: Finalize Payload")

    hold = st.checkbox("Hold if incomplete", True)
    creds = {
        "indeed": {
            "clientId": st.session_state.get("cid_indeed"),
            "clientSecret": st.session_state.get("csec_indeed")
        },
        "google": {
            "serviceAccountJson": st.session_state.get("gsa_google")
        }
    }

    payload = clean_dict({
        "url": url or None,
        "fields": job_fields,
        "modules": selected_ids or "all",
        "credentials": creds,
        "holdIfIncomplete": hold
    })

    st.subheader("Generated JSON Payload")
    st.code(json.dumps(payload, indent=2), language="json")

    if st.button("🚀 Submit to /api/jobs", use_container_width=True):
        with st.spinner("Sending request..."):
            status, resp = post_json(base_url, payload)
        st.write(f"Status: {status}")
        st.json(resp)

        if isinstance(resp, dict) and resp.get("status") == "held":
            st.success(f"✅ Job held for review: [Open Review]({resp.get('reviewUrl')})")
        elif isinstance(resp, dict) and resp.get("status") == "published":
            st.success("✅ Job published successfully!")

# ===================================================
# 2️⃣ RAW JSON TAB
# ===================================================
with tabs[1]:
    st.header("Raw JSON Input Mode")
    st.caption("Advanced users: directly enter full JSON payload for `/api/jobs`")
    payload_str = st.text_area("Payload JSON", "{\n  \"url\": \"\",\n  \"fields\": {},\n  \"modules\": \"all\"\n}", height=300)
    if st.button("Send Raw Payload"):
        try:
            payload = json.loads(payload_str)
            with st.spinner("Sending..."):
                status, resp = post_json(base_url, payload)
            st.write(f"Status: {status}")
            st.json(resp)
        except Exception as e:
            st.error(f"Invalid JSON: {e}")
