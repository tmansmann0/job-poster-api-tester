# Job Poster API Tester

This repository contains a Streamlit application that provides a user interface for interacting with the Job Poster API.

## Features

- Fetch and display available modules and their required fields.
- Accept a job URL for AI extraction or manually enter job fields.
- Supply per-request credentials for Indeed and Google.
- Select which modules to publish to or publish to all.
- Toggle whether to hold incomplete jobs for human review.
- Display raw JSON responses from the API.

## Running the app locally

1. Install the dependencies:
   pip install -r requirements.txt
2. Start the Streamlit application:
   streamlit run streamlit_app.py
3. Open your browser to http://localhost:8501

## Configuration

The app includes a sidebar where you can set the base URL of your Job Poster API (defaults to https://job-poster-r0c5.onrender.com). You can also enter per-request API keys to override default credentials.
