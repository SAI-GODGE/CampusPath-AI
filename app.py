
import re
import streamlit as st
from google import genai

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CampusPath AI | Placement Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CONFIGURATION
# =========================================================

DEFAULT_MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = """
You are CampusPath AI, a friendly college placement assistant.

Help students prepare for placements, technical interviews,
aptitude tests, resumes, projects, and job applications.

Rules:
- Use simple, clear language.
- Give practical steps and examples.
- Personalize answers using the student profile and conversation.
- Never guarantee job selection or eligibility.
- Never invent job requirements, salary figures, or deadlines.
- Clearly identify missing information.
- Use headings and bullet points where useful.
- Keep answers relevant and student-friendly.
"""


# =========================================================
# SESSION STATE
# =========================================================

def initialize_state():
    defaults = {
        "messages": [],
        "api_status": "Not tested",
        "last_api_error": "",
        "notice_result": "",
        "plan_result": "",
        "plan_offline": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()


# =========================================================
# API CONFIGURATION
# =========================================================

def get_api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        return str(key).strip() if key else ""
    except Exception:
        return ""


def get_model_name():
    try:
        model = st.secrets.get("GEMINI_MODEL", DEFAULT_MODEL)
        return str(model).strip() or DEFAULT_MODEL
    except Exception:
        return DEFAULT_MODEL


def sanitize_error(error):
    """Hide API keys from displayed diagnostic messages."""

    message = f"{type(error).__name__}: {error}"

    api_key = get_api_key()

    if api_key:
        message = message.replace(api_key, "[API KEY HIDDEN]")

    message = re.sub(
        r"AIza[0-9A-Za-z_-]{20,}",
        "[API KEY HIDDEN]",
        message,
    )

    return message[:1500]


def generate_ai_response(prompt, max_tokens=600):
    """Send a request to Gemini and return the generated text."""

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add it to "
            ".streamlit/secrets.toml."
        )

    client = genai.Client(api_key=api_key)
    model = get_model_name()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "max_output_tokens": max_tokens,
            "temperature": 0.3,
        },
    )

    answer = response.text

    if not answer or not answer.strip():
        raise RuntimeError(
            "Gemini returned an empty response. "
            "Check whether the request was blocked or returned no text."
        )

    st.session_state.api_status = "Connected"
    st.session_state.last_api_error = ""

    return answer.strip()


def explain_api_error(error):
    """Explain common API failures without hiding the technical error."""

    technical_error = sanitize_error(error)
    error_text = technical_error.lower()

    if (
        "429" in error_text
        or "resource_exhausted" in error_text
        or "quota" in error_text
        or "rate limit" in error_text
    ):
        explanation = (
            "A Gemini quota or rate limit may have been reached. "
            "Check your project's current API limits and try again "
            "after the limit resets."
        )

    elif (
        "401" in error_text
        or "403" in error_text
        or "permission_denied" in error_text
        or "unauthorized" in error_text
    ):
        explanation = (
            "The API key may be invalid, or the project may not have "
            "permission to use this API or model. Check your key and "
            "Google AI Studio project configuration."
        )

    elif (
        "404" in error_text
        or "not_found" in error_text
        or "not found" in error_text
    ):
        explanation = (
            "The selected model or endpoint may not be available. "
            "Check the currently supported Gemini API models and "
            "the model name in your secrets.toml file."
        )

    elif (
        "400" in error_text
        or "invalid_argument" in error_text
        or "bad request" in error_text
    ):
        explanation = (
            "Gemini rejected the request. Check the model name, "
            "request configuration, and SDK compatibility."
        )

    elif (
        "503" in error_text
        or "unavailable" in error_text
        or "timeout" in error_text
        or "connection" in error_text
        or "network" in error_text
    ):
        explanation = (
            "Gemini may be temporarily unavailable, or there may "
            "be a network connection problem. Try again later."
        )

    elif "api key" in error_text or "gemini_api_key" in error_text:
        explanation = (
            "Check that GEMINI_API_KEY exists in "
            ".streamlit/secrets.toml and contains a valid key."
        )

    else:
        explanation = (
            "The request failed for an unidentified reason. "
            "Read the technical error below for more details."
        )

    return explanation, technical_error


def display_api_error(error):
    """Display both a useful explanation and the technical error."""

    explanation, technical_error = explain_api_error(error)

    st.error("Gemini connection/request failed.")

    st.markdown("**Possible cause and next step:**")
    st.write(explanation)

    st.markdown("**Technical error:**")
    st.code(technical_error, language="text")


# =========================================================
# OFFLINE ASSISTANCE
# =========================================================

def local_help(question, profile):
    """Basic rule-based fallback. This is not an LLM response."""

    q = question.lower()

    degree = profile["degree"]
    cgpa = profile["cgpa"]
    backlogs = profile["backlogs"]
    skills = profile["skills"]
    target_role = profile["target_role"]

    if any(word in q for word in [
        "interview", "technical round", "technical interview"
    ]):
        return f"""
### Technical interview preparation

**1. Revise technical fundamentals**
- Data structures and algorithms
- Object-oriented programming
- Database management systems
- Operating systems
- Computer networks

**2. Practise coding**
- Solve 2–3 coding questions daily.
- Start with arrays, strings, sorting, and searching.
- Explain your approach before writing the solution.

**3. Prepare your projects**
- Explain the problem your project solves.
- Describe the tools and technologies you used.
- Explain your own contribution.
- Prepare to discuss one challenge and its solution.

**4. Practise communication**
- Prepare a 60–90 second self-introduction.
- Explain technical concepts in simple language.
- Practise mock interviews.

**Your profile**
- Degree: {degree}
- Skills: {skills or "Not provided"}
- Target role: {target_role}

**Today's goal:** Revise one technical subject and solve two coding
questions, then practise explaining one project aloud.
"""

    if any(word in q for word in [
        "resume", "cv", "curriculum vitae"
    ]):
        return """
### Resume improvement checklist

1. Keep your resume clear and concise.
2. Tailor the summary to the role you are applying for.
3. List relevant technical skills honestly.
4. Highlight projects, certifications, and practical experience.
5. Explain projects using the problem, your work, and the outcome.
6. Include accurate achievements rather than invented metrics.
7. Check spelling, dates, contact information, and links.

Prepare to explain every skill and project mentioned on your resume.
"""

    if any(word in q for word in [
        "aptitude", "reasoning", "quantitative"
    ]):
        return """
### Aptitude preparation plan

Focus on:
- Percentages, ratios, averages, and profit and loss
- Time and work
- Speed, distance, and time
- Number series and logical reasoning
- Verbal ability and reading comprehension

**Daily routine**
- 20 minutes learning a concept
- 30 minutes solving timed questions
- 10 minutes reviewing mistakes

Keep a record of difficult questions and revisit them regularly.
"""

    if any(word in q for word in [
        "placement", "job", "company", "career", "fresher"
    ]):
        return f"""
### Your placement action plan

**Step 1:** Identify entry-level roles that match your interests.

**Step 2:** Revise the technical fundamentals required for those roles.

**Step 3:** Practise coding, aptitude, or role-specific technical tasks.

**Step 4:** Improve your resume and prepare project explanations.

**Step 5:** Track company names, job requirements, deadlines, and
application status.

**Your current profile**
- Degree: {degree}
- CGPA: {cgpa}
- Backlogs: {backlogs}
- Skills: {skills or "Not provided"}
- Target role: {target_role}

Verify the exact requirements on each employer's official notice.
"""

    return """
### Placement preparation guidance

Start with these actions:

1. Revise core technical subjects.
2. Practise coding or role-specific exercises.
3. Prepare your resume and project explanations.
4. Practise aptitude and communication.
5. Track job notices and application deadlines.

You can ask a more specific question, such as:
- How should I prepare for a technical interview?
- How can I improve my resume?
- Give me a 7-day aptitude preparation plan.
- Help me explain my final-year project.
"""


def local_notice_analysis(notice):
    """Checklist fallback when the Gemini API is unavailable."""

    return f"""
### Job notice review — offline mode

Gemini was unavailable, so this is a basic checklist rather than
AI-generated analysis.

Review the original notice for:

- Company and job title
- Eligible degrees and branches
- Graduation year
- Minimum CGPA or percentage
- Active or permitted backlogs
- Required and preferred skills
- Work location
- Salary or stipend, if stated
- Application deadline
- Official application link
- Documents required for application

Notice length: {len(notice)} characters.

**Important:** The notice has not been fully analyzed by the AI service.
Verify every condition against the original employer announcement.
"""


# =========================================================
# SIDEBAR: STUDENT PROFILE
# =========================================================

st.sidebar.title("🎓 CampusPath AI")
st.sidebar.caption("Your college placement companion")

st.sidebar.subheader("Student Profile")

student_name = st.sidebar.text_input(
    "Name (optional)",
    placeholder="Enter your name",
)

degree = st.sidebar.text_input(
    "Degree / Branch",
    value="B.Tech Computer Science and Engineering",
)

cgpa = st.sidebar.number_input(
    "CGPA",
    min_value=0.0,
    max_value=10.0,
    value=7.0,
    step=0.1,
)

backlogs = st.sidebar.number_input(
    "Current backlogs",
    min_value=0,
    max_value=50,
    value=0,
    step=1,
)

skills = st.sidebar.text_area(
    "Technical skills",
    value="Python, Linux, AWS, SQL",
    help="Separate skills with commas.",
)

target_role = st.sidebar.text_input(
    "Target role",
    value="Graduate / Entry-Level Technical Role",
)

profile = {
    "name": student_name,
    "degree": degree,
    "cgpa": cgpa,
    "backlogs": backlogs,
    "skills": skills,
    "target_role": target_role,
}

profile_text = f"""
Student profile:
Name: {student_name or "Not provided"}
Degree: {degree}
CGPA: {cgpa}
Current backlogs: {backlogs}
Technical skills: {skills}
Target role: {target_role}
"""


# =========================================================
# SIDEBAR: API STATUS AND DIAGNOSTICS
# =========================================================

st.sidebar.divider()
st.sidebar.subheader("AI Service Status")

if st.session_state.api_status == "Connected":
    st.sidebar.success("Gemini connected")
elif st.session_state.api_status == "Unavailable":
    st.sidebar.error("Gemini connection failed")
else:
    st.sidebar.info("Gemini has not been tested in this session.")

st.sidebar.caption(f"Selected model: {get_model_name()}")

if st.sidebar.button(
    "Test Gemini Connection",
    use_container_width=True,
):
    try:
        with st.spinner("Testing Gemini connection..."):
            test_answer = generate_ai_response(
                "Reply with exactly: Gemini connection successful.",
                max_tokens=30,
            )

        st.sidebar.success("Gemini API is responding.")
        st.sidebar.write(test_answer)

    except Exception as error:
        st.session_state.api_status = "Unavailable"
        st.session_state.last_api_error = sanitize_error(error)

        # FIX: Show the real technical error instead of hiding it.
        explanation, technical_error = explain_api_error(error)

        st.sidebar.error("Gemini connection failed.")

        st.sidebar.markdown("**Possible cause and next step:**")
        st.sidebar.write(explanation)

        st.sidebar.markdown("**Technical error:**")
        st.sidebar.code(technical_error, language="text")

if st.sidebar.button(
    "Clear Chat History",
    use_container_width=True,
):
    st.session_state.messages = []
    st.rerun()

st.sidebar.divider()
st.sidebar.caption(
    "Offline responses use basic local rules and are not generated "
    "by Gemini."
)


# =========================================================
# MAIN HEADER
# =========================================================

st.title("🎓 CampusPath AI")
st.subheader("AI College Placement Assistant")

st.write(
    "Prepare for placements, practise interviews, review job notices, "
    "and build a structured preparation plan."
)

st.divider()


# =========================================================
# NAVIGATION
# =========================================================

page = st.radio(
    "Choose a feature",
    [
        "Placement Chat",
        "Job Notice Analysis",
        "Eligibility Checker",
        "Preparation Plan",
    ],
    horizontal=True,
    label_visibility="collapsed",
)


# =========================================================
# FEATURE 1: PLACEMENT CHAT
# =========================================================

if page == "Placement Chat":

    st.header("💬 Placement Chat")

    st.caption(
        "Ask about interviews, resumes, aptitude, projects, "
        "or placement preparation."
    )

    if not st.session_state.messages:
        st.info(
            "Try asking: How should I prepare for a technical interview "
            "as a computer science student?"
        )

    # Display previous messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("offline", False):
                st.caption("Offline rule-based assistance")

    question = st.chat_input(
        "Ask your placement-related question..."
    )

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question,
        })

        with st.chat_message("user"):
            st.markdown(question)

        # Limit the amount of conversation sent to Gemini.
        recent_messages = st.session_state.messages[-10:]

        conversation = "\n".join(
            f'{message["role"].upper()}: {message["content"]}'
            for message in recent_messages
        )

        prompt = f"""
{profile_text}

Recent conversation:
{conversation}

Answer the student's latest question.
Use the profile and previous conversation where relevant.
"""

        with st.chat_message("assistant"):

            with st.spinner("Preparing your answer..."):

                try:
                    answer = generate_ai_response(
                        prompt,
                        max_tokens=600,
                    )
                    is_offline = False
                    api_error = None

                except Exception as error:
                    st.session_state.api_status = "Unavailable"
                    st.session_state.last_api_error = sanitize_error(error)

                    answer = local_help(question, profile)
                    is_offline = True
                    api_error = error

            st.markdown(answer)

            if is_offline:
                st.warning(
                    "Gemini is unavailable. This is offline assistance, "
                    "not an AI-generated answer."
                )

                with st.expander("View Gemini diagnostic details"):
                    explanation, technical_error = explain_api_error(
                        api_error
                    )
                    st.write(explanation)
                    st.code(technical_error, language="text")

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "offline": is_offline,
            })


# =========================================================
# FEATURE 2: JOB NOTICE ANALYSIS
# =========================================================

elif page == "Job Notice Analysis":

    st.header("📄 Job Notice Analysis")

    st.write(
        "Paste a recruitment notice to review its stated requirements, "
        "skills, deadlines, and application steps."
    )

    notice = st.text_area(
        "Paste the job description or recruitment notice",
        height=260,
        placeholder=(
            "Paste the company name, role, qualification, CGPA, "
            "backlog rules, skills, deadline, and application details..."
        ),
    )

    if st.button("Analyze Job Notice", type="primary"):

        if not notice.strip():
            st.warning("Please paste a job notice first.")

        else:
            notice_prompt = f"""
Analyze the recruitment notice using the student profile.

{profile_text}

Return the result in these sections:

1. Company and job role, if stated
2. Required degree, branch, and graduation year
3. CGPA or percentage requirements
4. Backlog conditions
5. Required and preferred skills
6. Location, salary, and deadline, if stated
7. Application steps and required documents
8. Preliminary eligibility assessment
9. Missing information to verify
10. Recommended next steps

Do not invent missing information.
Separate stated facts from assumptions.
Do not guarantee eligibility.
For missing information, write "Not specified in the notice."

Recruitment notice:
{notice}
"""

            with st.spinner("Analyzing the notice..."):

                try:
                    result = generate_ai_response(
                        notice_prompt,
                        max_tokens=1000,
                    )

                    st.session_state.notice_result = result

                except Exception as error:
                    st.session_state.api_status = "Unavailable"
                    st.session_state.last_api_error = sanitize_error(error)

                    st.session_state.notice_result = local_notice_analysis(
                        notice
                    )

                    st.warning(
                        "Gemini is unavailable. Showing a basic offline "
                        "checklist instead of AI notice analysis."
                    )

                    with st.expander("View Gemini diagnostic details"):
                        explanation, technical_error = explain_api_error(
                            error
                        )
                        st.write(explanation)
                        st.code(technical_error, language="text")

    if st.session_state.notice_result:
        st.divider()
        st.subheader("Analysis Result")
        st.markdown(st.session_state.notice_result)


# =========================================================
# FEATURE 3: ELIGIBILITY CHECKER
# =========================================================

elif page == "Eligibility Checker":

    st.header("✅ Placement Eligibility Checker")

    st.write(
        "Check the requirements you enter. This feature works locally "
        "and does not require Gemini."
    )

    col1, col2 = st.columns(2)

    with col1:
        required_cgpa = st.number_input(
            "Minimum required CGPA",
            min_value=0.0,
            max_value=10.0,
            value=6.0,
            step=0.1,
        )

        max_backlogs = st.number_input(
            "Maximum allowed current backlogs",
            min_value=0,
            max_value=50,
            value=0,
            step=1,
        )

    with col2:
        required_degree = st.selectbox(
            "Degree requirement",
            [
                "Any degree",
                "B.Tech / B.E.",
                "Computer Science / IT",
            ],
        )

        required_skills = st.text_input(
            "Required skills (comma-separated)",
            placeholder="Python, SQL, Linux",
        )

    if st.button("Check Eligibility", type="primary"):

        results = []
        issues = []

        cgpa_pass = cgpa >= required_cgpa
        backlog_pass = backlogs <= max_backlogs

        if cgpa_pass:
            results.append(
                f"CGPA: {cgpa:.1f} meets the entered minimum "
                f"of {required_cgpa:.1f}."
            )
        else:
            issues.append(
                f"CGPA: {cgpa:.1f} is below the entered minimum "
                f"of {required_cgpa:.1f}."
            )

        if backlog_pass:
            results.append(
                f"Backlogs: {backlogs} meets the entered maximum "
                f"of {max_backlogs}."
            )
        else:
            issues.append(
                f"Backlogs: {backlogs} exceeds the entered maximum "
                f"of {max_backlogs}."
            )

        degree_lower = degree.lower()
        degree_pass = True

        if required_degree == "B.Tech / B.E.":
            degree_pass = (
                "b.tech" in degree_lower
                or "btech" in degree_lower
                or "b.e" in degree_lower
                or "bachelor of engineering" in degree_lower
            )

        elif required_degree == "Computer Science / IT":
            degree_pass = any(
                term in degree_lower
                for term in [
                    "computer science",
                    "cse",
                    "information technology",
                ]
            )

        if degree_pass:
            results.append(
                f"Degree: matches the selected requirement "
                f"({required_degree})."
            )
        else:
            issues.append(
                f"Degree: your entered degree may not match "
                f"{required_degree}. Verify the employer's exact rules."
            )

        skills_pass = True

        if required_skills.strip():
            student_skills = {
                item.strip().lower()
                for item in skills.split(",")
                if item.strip()
            }

            missing_skills = [
                item.strip()
                for item in required_skills.split(",")
                if item.strip()
                and item.strip().lower() not in student_skills
            ]

            if missing_skills:
                skills_pass = False
                issues.append(
                    "Skills not found in your profile: "
                    + ", ".join(missing_skills)
                    + ". This is a simple text comparison."
                )
            else:
                results.append(
                    "All entered required skills appear in your profile."
                )

        if cgpa_pass and backlog_pass and degree_pass and skills_pass:
            st.success(
                "You meet the requirements entered in this checker."
            )
        else:
            st.warning(
                "One or more entered requirements may not be met."
            )

        st.subheader("Results")

        for item in results:
            st.write(f"- {item}")

        for item in issues:
            st.write(f"- {item}")

        st.info(
            "This is a preliminary local check, not an official "
            "eligibility decision. Verify graduation year, branch rules, "
            "academic history, and every condition in the original notice."
        )


# =========================================================
# FEATURE 4: PREPARATION PLAN
# =========================================================

elif page == "Preparation Plan":

    st.header("🗓️ Placement Preparation Plan")

    st.write(
        "Build a preparation plan based on your current skills "
        "and target role."
    )

    col1, col2 = st.columns(2)

    with col1:
        duration = st.selectbox(
            "Plan duration",
            ["7 days", "14 days", "30 days"],
        )

    with col2:
        daily_hours = st.selectbox(
            "Available study time per day",
            ["1 hour", "2 hours", "3 hours", "4+ hours"],
            index=1,
        )

    focus = st.multiselect(
        "Areas to focus on",
        [
            "Technical fundamentals",
            "Coding practice",
            "Aptitude and reasoning",
            "Resume and projects",
            "Mock interviews",
            "Communication skills",
        ],
        default=[
            "Technical fundamentals",
            "Resume and projects",
            "Mock interviews",
        ],
    )

    if st.button("Generate Preparation Plan", type="primary"):

        plan_prompt = f"""
Create a realistic placement preparation plan.

{profile_text}

Duration: {duration}
Available study time per day: {daily_hours}
Focus areas: {", ".join(focus) if focus else "General preparation"}

Requirements:
- Organize the plan by day or week.
- Give concrete tasks for each study session.
- Include practice and revision.
- Include measurable progress checks.
- Adapt the plan to the student's target role and skills.
- Use simple language and realistic workloads.
"""

        with st.spinner("Creating your preparation plan..."):

            try:
                st.session_state.plan_result = generate_ai_response(
                    plan_prompt,
                    max_tokens=1400,
                )

                st.session_state.plan_offline = False

            except Exception as error:
                st.session_state.api_status = "Unavailable"
                st.session_state.last_api_error = sanitize_error(error)

                selected_focus = (
                    "\n".join("- " + item for item in focus)
                    if focus
                    else "- Revise core technical subjects"
                )

                st.session_state.plan_result = f"""
### {duration} offline preparation plan

**Degree:** {degree}

**Target role:** {target_role}

**Daily study time:** {daily_hours}

**Suggested focus areas**
{selected_focus}

**Daily routine**
1. Revise one technical concept.
2. Solve practice questions related to that concept.
3. Work on your resume or project explanation.
4. Review mistakes and record your progress.

**Progress tracking**
- Record the topics completed each day.
- Track coding problems solved and mistakes corrected.
- Practise explaining your projects aloud.
- Take mock interviews regularly.
- Adjust your next session based on weak areas.

Gemini was unavailable, so this is a basic offline plan rather than
an AI-generated day-by-day schedule.
"""

                st.session_state.plan_offline = True

                st.warning(
                    "Gemini is unavailable. Showing a basic offline plan."
                )

                with st.expander("View Gemini diagnostic details"):
                    explanation, technical_error = explain_api_error(
                        error
                    )
                    st.write(explanation)
                    st.code(technical_error, language="text")

    if st.session_state.plan_result:
        st.divider()
        st.subheader("Your Preparation Plan")
        st.markdown(st.session_state.plan_result)

        if st.session_state.plan_offline:
            st.caption("Basic offline plan")


# =========================================================
# END OF APPLICATION
# =========================================================
