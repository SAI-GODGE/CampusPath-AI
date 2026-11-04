
# CampusPath AI — AI College Placement Assistant

An AI-powered placement assistant that helps students prepare for campus recruitment with placement guidance, job notice analysis, eligibility checks, and preparation plans.

**Live Demo:** [Open CampusPath AI](https://campuspath-ai.streamlit.app/)

## Features

- **Placement Chat** — Get placement-related guidance and answers to career preparation questions.
- **Job Notice Analysis** — Review job descriptions and identify key role requirements.
- **Eligibility Checker** — Check eligibility against provided job criteria.
- **Preparation Plan** — Generate a structured plan for placement preparation.
- **AI-Powered Responses** — Uses the Gemini API for conversational assistance.

## Tech Stack

- Python
- Streamlit
- Google Gemini API

## Run Locally

1. Clone the repository:

   ```bash
   git clone YOUR_GITHUB_REPOSITORY_URL
   cd CampusPath-AI
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   macOS / Linux:

   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure your Gemini API key using Streamlit secrets. Create `.streamlit/secrets.toml` locally:

   ```toml
   GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
   ```

   **Do not commit this file or expose your API key publicly.**

5. Start the app:

   ```bash
   streamlit run app.py
   ```

## Project Structure

```text
CampusPath-AI/
├── app.py
├── requirements.txt
└── README.md
```

*Add any other project files or folders here if your repository includes them.*

## Deployment

CampusPath AI is deployed on **Streamlit Community Cloud**. Open the live demo link above to try the application.

## Disclaimer

CampusPath AI provides informational support for placement preparation. Verify job requirements, eligibility criteria, and recruitment details with the official employer or placement office.

## Author

**Saiprasad Godge**  
Computer Science and Engineering Student


















CampusPath-AI : https://campuspath-ai.streamlit.app/
