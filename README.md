<div align="center">

# CampusPath AI

### AI College Placement Assistant

An AI-powered assistant that helps students prepare for campus recruitment through placement guidance, job-description analysis, eligibility checks, and personalized preparation plans.

[**CampusPath-AI**](https://campuspath-ai.streamlit.app/) · [**View Source Code**](YOUR_GITHUB_REPOSITORY_URL)

</div>

---

## Overview

CampusPath AI brings essential placement-preparation tools into one simple interface. Students can explore career guidance, understand job requirements, check eligibility against provided criteria, and create a focused preparation plan.

The application uses **Streamlit** for its interactive interface and the **Google Gemini API** for AI-powered assistance.

## What You Can Do

| Feature | Description |
|---|---|
| **Placement Chat** | Ask placement and career-preparation questions. |
| **Job Notice Analysis** | Review a job notice and identify important role requirements. |
| **Eligibility Checker** | Compare provided details with stated job criteria. |
| **Preparation Plan** | Create a structured plan for placement preparation. |

## Try It

**[Open CampusPath AI →](YOUR_DEPLOYED_APP_URL)**

The application is hosted on Streamlit Community Cloud. Open the live app to explore its features.

## Technology

`Python` · `Streamlit` · `Google Gemini API`

## Run Locally

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd CampusPath-AI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your Gemini API key

Create `.streamlit/secrets.toml` and add your key:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Keep this file private. **Never commit API keys or secrets to GitHub.**

### 5. Start the app

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

*Add any other files or folders that are part of your repository.*

## Deployment

CampusPath AI is deployed using **Streamlit Community Cloud**. The live application is available through the demo link at the top of this README.

## Note

CampusPath AI is intended to support placement preparation. Always confirm job requirements, eligibility rules, and recruitment details with the official employer or placement office.

---

<div align="center">

Built as a student project by **Saiprasad Godge**  
Computer Science and Engineering

</div>
