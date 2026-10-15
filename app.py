import os
import json
import html
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from services.pdf_parser import extract_pdf_text
from services.resume_extractor import clean_resume_text
from chains.ats_chain import analyze_resume
from chains.skill_chain import extract_skills_from_resume_chain
from chains.interview_chain import generate_question_chain
from chains.evaluation_chain import evaluate_answer_chain
from chains.rewrite_chain import rewrite_resume_chain
from chains.format_chain import format_resume_chain


# ----------------------------- Configuration -----------------------------
st.set_page_config(
    page_title="AI Resume Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        temperature=0.2,
        max_output_tokens=2048,
    )
else:
    llm = None

SECTIONS = ["ATS Analysis", "Skills Explorer", "Mock Interview", "Resume Studio"]

DEFAULT_STATE = {
    "resume_text": None,
    "ats": None,
    "skills": None,
    "source_file": None,
    "current_question": None,
    "latest_evaluation": None,
    "questions": [],
    "answers": [],
    "evaluations": [],
    "total_score": 0,
    "rewritten_resume": None,
    "html_resume": None,
    "resume_job_role": "",
    "resume_job_description": "",
}
for key, default in DEFAULT_STATE.items():
    if key not in st.session_state:
        # Avoid sharing mutable default lists between sessions.
        st.session_state[key] = default.copy() if isinstance(default, list) else default


# ---------------------------------- Style ---------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root {
        --ink: #172033; --muted: #64748b; --violet: #7357f6;
        --violet-dark: #5b3de8; --line: #e7eaf2; --panel: #ffffff;
    }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f7f8ff 0%, #f5f7fb 52%, #f2fbf8 100%); color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(247,248,255,0.82); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #17152e 0%, #242044 55%, #2c2851 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] * { color: #f5f4ff; }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] section {
        background: rgba(255,255,255,0.08); border: 1px dashed rgba(255,255,255,0.34); border-radius: 14px;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] small { color: #d4d1ed !important; }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] button { color: #282044 !important; }
    h1, h2, h3 { font-family: 'Manrope', sans-serif !important; letter-spacing: -0.035em; }
    h1 { color: #17152e; font-weight: 800 !important; }
    h2, h3 { color: #242044; font-weight: 750 !important; }
    p, li { color: #354158; }
    .hero {
        padding: 1.65rem 1.8rem; border-radius: 24px;
        background: linear-gradient(120deg, #262047 0%, #5742b5 62%, #7765ed 100%);
        color: white; box-shadow: 0 16px 40px rgba(55, 42, 120, 0.18);
        margin: 0.15rem 0 1.4rem 0; position: relative; overflow: hidden;
    }
    .hero:after {
        content: ''; position: absolute; width: 220px; height: 220px;
        border: 1px solid rgba(255,255,255,0.15); border-radius: 50%;
        right: -45px; top: -105px;
        box-shadow: 0 0 0 24px rgba(255,255,255,0.04), 0 0 0 52px rgba(255,255,255,0.035);
    }
    .hero-kicker { color: #dcd6ff; text-transform: uppercase; letter-spacing: .16em; font-size: .73rem; font-weight: 700; }
    .hero-title { color: #fff; font-family: 'Manrope', sans-serif; font-size: clamp(1.8rem, 3vw, 2.6rem); font-weight: 800; line-height: 1.15; margin: .35rem 0 .5rem; }
    .hero-subtitle { color: #efedff; max-width: 760px; margin: 0; font-size: 1rem; }
    .eyebrow { color: #7868d8; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; font-size: .72rem; margin-bottom: .25rem; }
    .panel {
        border: 1px solid var(--line); background: rgba(255,255,255,0.88);
        border-radius: 18px; padding: 1.15rem 1.25rem;
        box-shadow: 0 8px 24px rgba(31, 41, 71, 0.045); margin-bottom: .85rem;
    }
    .panel-title { font-family: 'Manrope', sans-serif; color: #252044; font-weight: 800; font-size: 1.05rem; margin-bottom: .45rem; }
    .panel-caption { color: #738096; font-size: .9rem; }
    .pill { display: inline-block; padding: .28rem .65rem; border-radius: 999px; background: #eeeaff; color: #5942c5; font-size: .78rem; font-weight: 700; margin: .15rem .2rem .15rem 0; }
    .skill-chip { display: inline-block; padding: .35rem .65rem; margin: .2rem .25rem .2rem 0; background: #f0efff; color: #4e3da5; border: 1px solid #e2defe; border-radius: 9px; font-size: .83rem; font-weight: 600; }
    div[data-testid="stMetric"] { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 1rem 1.1rem; box-shadow: 0 8px 22px rgba(31,41,71,.04); }
    div[data-testid="stMetricLabel"] { color: #778198; font-weight: 600; }
    div[data-testid="stMetricValue"] { color: #282044; font-family: 'Manrope', sans-serif; }
    .stButton > button, .stDownloadButton > button {
        border-radius: 11px; border: 1px solid #d9d4ff; padding: .55rem 1rem; font-weight: 700; transition: all .18s ease;
    }
    .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
        background: linear-gradient(110deg, #7357f6, #5c42d6); color: white; border: 0; box-shadow: 0 7px 16px rgba(104,79,224,.22);
    }
    .stButton > button:hover, .stDownloadButton > button:hover { border-color: #8b7bf7; transform: translateY(-1px); }
    [data-testid="stExpander"] { background: rgba(255,255,255,.84); border: 1px solid var(--line); border-radius: 14px; }
    [data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input { border-radius: 13px; border-color: #dfe3ef; background: #fff; }
    [data-testid="stRadio"] label { font-weight: 600; }
    hr { border-color: #e5e7f0; }
    .footer-note { text-align: center; color: #8992a6; font-size: .78rem; padding: 1.5rem 0 .5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def hero(kicker: str, title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">{html.escape(kicker)}</div>
            <div class="hero-title">{html.escape(title)}</div>
            <p class="hero-subtitle">{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(eyebrow: str, title: str, subtitle: str = ""):
    st.markdown(f'<div class="eyebrow">{html.escape(eyebrow)}</div>', unsafe_allow_html=True)
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)


def run_analysis(cleaned_text, model):
    ats_response = analyze_resume(cleaned_text, model)
    skills_chain = extract_skills_from_resume_chain(cleaned_text, model)
    skills_response = skills_chain.invoke({})
    st.session_state.ats = ats_response
    st.session_state.skills = skills_response
    return ats_response, skills_response


def render_ats(ats_response):
    hero("Resume intelligence", "Your ATS snapshot", "A clear, actionable view of how your resume communicates your experience.")
    score = max(0, min(100, int(ats_response.ats_score)))
    score_col, summary_col = st.columns([1, 2], gap="large")
    with score_col:
        st.markdown('<div class="panel-title">ATS compatibility</div>', unsafe_allow_html=True)
        st.metric("Resume score", f"{score}/100")
        st.progress(score / 100)
        label = "Strong match" if score >= 80 else "Good foundation" if score >= 60 else "Room to improve"
        st.markdown(f'<span class="pill">{label}</span>', unsafe_allow_html=True)
    with summary_col:
        st.markdown('<div class="panel-title">Recruiter-style summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="panel">{html.escape(str(ats_response.summary))}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    groups = [
        (col1, "✅ Strengths", ats_response.strengths, "No strengths were returned."),
        (col1, "🧭 Improvements", ats_response.improvements, "No improvement suggestions were returned."),
        (col2, "🔎 Weaknesses / gaps", ats_response.weaknesses, "No weaknesses were returned."),
        (col2, "🧩 Missing keywords", ats_response.missing_keywords, "No missing keywords were identified."),
    ]
    for column, title, items, empty_text in groups:
        with column:
            with st.container(border=True):
                st.markdown(f"### {title}")
                if items:
                    if title.startswith("🧩"):
                        chips = " ".join(f'<span class="skill-chip">{html.escape(str(item))}</span>' for item in items)
                        st.markdown(chips, unsafe_allow_html=True)
                    else:
                        for item in items:
                            st.markdown(f"- {item}")
                else:
                    st.caption(empty_text)


def render_skills(skills_result):
    candidate = skills_result.candidate_name or "Candidate profile"
    role = skills_result.target_role or "Role not inferred"
    hero("Skill intelligence", "Your technical toolkit", "Explore technologies detected in your resume, along with the evidence behind each one.")
    st.markdown(
        f'<span class="pill">👤 {html.escape(str(candidate))}</span> <span class="pill">🎯 {html.escape(str(role))}</span>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="panel-title">Profile summary</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="panel">{html.escape(str(skills_result.extraction_summary))}</div>', unsafe_allow_html=True)

    skill_groups = {
        "Programming languages": skills_result.skills.programming_languages,
        "Frameworks & libraries": skills_result.skills.frameworks_and_libraries,
        "Databases": skills_result.skills.databases,
        "Cloud & DevOps": skills_result.skills.cloud_and_devops,
        "Tools & platforms": skills_result.skills.tools_and_platforms,
        "AI & ML": skills_result.skills.ai_and_ml,
        "Domains & concepts": skills_result.skills.domains_and_concepts,
        "APIs & protocols": skills_result.skills.apis_and_protocols,
    }
    total_skills = sum(len(items) for items in skill_groups.values())
    st.metric("Skills identified", total_skills)
    section_heading("Detected experience", "Skills by category", "Expand a category to see confidence, usage signal, and resume evidence.")
    for group_name, items in skill_groups.items():
        if not items:
            continue
        with st.expander(f"{group_name} · {len(items)} skills"):
            for skill in items:
                st.markdown(f"**{skill.name}** · `{skill.confidence.value}` · `{skill.proficiency_signal.value}`")
                if hasattr(skill, "type"):
                    st.caption(f"Category: {skill.type.value}")
                if hasattr(skill, "category"):
                    st.caption(f"Category: {skill.category.value}")
                st.caption(f"Evidence: {skill.evidence}")
                st.divider()

    if skills_result.interview_focus_areas:
        section_heading("Interview preparation", "Topics worth revising", "Prioritized from skills and experience found in your resume.")
        focus_cols = st.columns(2, gap="medium")
        for idx, focus in enumerate(skills_result.interview_focus_areas):
            with focus_cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"**🎯 {focus.skill}**")
                    st.caption(f"Suggested depth: {focus.suggested_depth.value}")
                    st.write(focus.reason)

    if skills_result.skills_flat_list:
        section_heading("Quick scan", "All extracted skills")
        chips = " ".join(f'<span class="skill-chip">{html.escape(str(skill))}</span>' for skill in skills_result.skills_flat_list)
        st.markdown(chips, unsafe_allow_html=True)


def render_questions():
    hero("Practice mode", "Mock interview", "Practice one question at a time, get structured feedback, and track your progress.")
    render_progress_metric()
    if st.session_state.skills is None:
        st.warning("Upload and analyze a resume before starting a mock interview.")
        return

    start_col, info_col = st.columns([1, 2], gap="large")
    with start_col:
        if st.button("✨ Start / Restart interview", type="primary", use_container_width=True):
            st.session_state.questions = []
            st.session_state.answers = []
            st.session_state.evaluations = []
            st.session_state.total_score = 0
            st.session_state.latest_evaluation = None
            st.session_state.current_question = None
            st.session_state.answer_input = ""
            try:
                with st.spinner("Preparing your first question..."):
                    question = generate_question_chain(
                        name=st.session_state.skills.candidate_name or "Candidate",
                        role=st.session_state.skills.target_role or "Target Role",
                        skills=st.session_state.skills.skills_flat_list,
                        previous_questions=[],
                        llm=llm,
                    ).invoke({})
                st.session_state.current_question = question
                st.session_state.questions.append(question.question)
                st.rerun()
            except Exception as exc:
                st.error(f"Could not generate an interview question: {exc}")
    with info_col:
        st.markdown(
            '<div class="panel"><div class="panel-title">How it works</div>'
            '<div class="panel-caption">Answer naturally, submit your response, and review feedback on technical accuracy, clarity, strengths, and areas to improve.</div></div>',
            unsafe_allow_html=True,
        )

    question = st.session_state.current_question
    if question:
        st.markdown('<div class="eyebrow">Your next challenge</div>', unsafe_allow_html=True)
        with st.container(border=True):
            top1, top2 = st.columns([3, 1])
            with top1:
                st.markdown("### Interview question")
            with top2:
                st.markdown(f'<span class="pill">{html.escape(str(question.difficulty.value))}</span>', unsafe_allow_html=True)
            st.write(question.question)
            answer = st.text_area(
                "Your answer", key="answer_input", height=180,
                placeholder="Structure your answer, explain your reasoning, and use examples from your experience...",
            )
            if st.button("Submit answer & get feedback", type="primary", use_container_width=True):
                if not answer.strip():
                    st.warning("Write an answer before submitting it.")
                    return
                try:
                    with st.spinner("Evaluating your answer..."):
                        evaluation = evaluate_answer_chain(
                            question=question.question, answer=answer,
                            difficulty=question.difficulty, llm=llm,
                        ).invoke({})
                    st.session_state.answers.append(answer)
                    st.session_state.evaluations.append(evaluation)
                    st.session_state.total_score += evaluation.overall_score
                    st.session_state.latest_evaluation = evaluation

                    with st.spinner("Preparing your next question..."):
                        next_question = generate_question_chain(
                            name=st.session_state.skills.candidate_name or "Candidate",
                            role=st.session_state.skills.target_role or "Target Role",
                            skills=st.session_state.skills.skills_flat_list,
                            previous_questions=st.session_state.questions,
                            llm=llm,
                        ).invoke({})
                    st.session_state.current_question = next_question
                    st.session_state.questions.append(next_question.question)
                    st.session_state.answer_input = ""
                    st.rerun()
                except Exception as exc:
                    st.error(f"Unable to evaluate your answer or generate the next question: {exc}")

    if st.session_state.latest_evaluation is not None:
        render_result(st.session_state.latest_evaluation)
    render_questions_history()


def render_progress_metric():
    completed = len(st.session_state.answers)
    avg_score = st.session_state.total_score / completed if completed else 0
    col1, col2, col3 = st.columns(3, gap="medium")
    col1.metric("Questions answered", completed)
    col2.metric("Average score", f"{avg_score:.1f}/10" if completed else "—")
    col3.metric("Total points", st.session_state.total_score)
    st.progress(min(completed / 10, 1.0), text=f"Practice progress · {completed}/10 answers")


def render_result(evaluation):
    section_heading("Answer feedback", "Your evaluation", "Use this feedback to strengthen your next answer.")
    c1, c2, c3 = st.columns(3, gap="medium")
    c1.metric("Overall score", f"{evaluation.overall_score}/10")
    c2.metric("Technical accuracy", f"{evaluation.technical_accuracy}/10")
    c3.metric("Clarity", f"{evaluation.clarity}/10")
    left, right = st.columns(2, gap="large")
    with left:
        with st.container(border=True):
            st.markdown("### ✅ What worked")
            for item in evaluation.strengths:
                st.markdown(f"- {item}")
        with st.container(border=True):
            st.markdown("### 💡 How to improve")
            for item in evaluation.improvements:
                st.markdown(f"- {item}")
    with right:
        with st.container(border=True):
            st.markdown("### 🛠️ Gaps to address")
            for item in evaluation.weaknesses:
                st.markdown(f"- {item}")
        with st.expander("View an example of a strong answer"):
            st.write(evaluation.ideal_answer)


def render_questions_history():
    completed = list(zip(
        st.session_state.questions[:len(st.session_state.answers)],
        st.session_state.answers,
        st.session_state.evaluations,
    ))
    if not completed:
        return
    with st.expander(f"📚 Interview history · {len(completed)} completed"):
        for idx, (question_text, answer, evaluation) in enumerate(completed, start=1):
            st.markdown(f"**Question {idx}** · Score: `{evaluation.overall_score}/10`")
            st.write(question_text)
            st.markdown("**Your answer**")
            st.write(answer)
            st.divider()


def resume_to_display_text(resume):
    if hasattr(resume, "model_dump_json"):
        return resume.model_dump_json(indent=2)
    if isinstance(resume, dict):
        return json.dumps(resume, indent=2, ensure_ascii=False)
    return str(resume)


def render_resume_studio():
    hero(
        "Career toolkit", "Resume Studio",
        "Tailor your resume to a target role, review the result, and export a polished HTML version.",
    )
    if st.session_state.skills is None or st.session_state.ats is None:
        st.warning("Upload and analyze your resume before using Resume Studio.")
        return

    section_heading("Step 01 · Personalize", "Tell us about the opportunity",
                    "Provide the target role and job description to tailor your resume.")
    with st.container(border=True):
        with st.form("resume_studio_form"):
            job_role = st.text_input(
                "Target job role", value=st.session_state.resume_job_role,
                placeholder="e.g. Software Development Engineer",
            )
            job_description = st.text_area(
                "Job description", value=st.session_state.resume_job_description,
                height=190, placeholder="Paste the responsibilities, requirements, and skills here...",
            )
            submitted = st.form_submit_button(
                "✨ Tailor my resume", type="primary", use_container_width=True,
            )

    if submitted:
        if not job_role.strip() or not job_description.strip():
            st.warning("Please enter both the target role and job description.")
        else:
            st.session_state.resume_job_role = job_role.strip()
            st.session_state.resume_job_description = job_description.strip()
            try:
                with st.spinner("Tailoring your resume to the role..."):
                    rewritten = rewrite_resume_chain(
                        resume=st.session_state.resume_text,
                        ats=st.session_state.ats,
                        skills=st.session_state.skills.skills_flat_list,
                        job_role=st.session_state.resume_job_role,
                        job_description=st.session_state.resume_job_description,
                        llm=llm,
                    ).invoke({})
                st.session_state.rewritten_resume = rewritten
                st.session_state.html_resume = None
                st.success("Your tailored resume is ready.")
            except Exception as exc:
                st.error(f"Unable to rewrite the resume: {exc}")

    rewritten = st.session_state.rewritten_resume
    if rewritten is None:
        st.markdown(
            '<div class="panel"><div class="panel-title">✨ Your next step</div>'
            '<div class="panel-caption">Enter a role and job description above. You can review the rewritten content before generating the HTML resume.</div></div>',
            unsafe_allow_html=True,
        )
        return

    section_heading("Step 02 · Review", "Review your tailored content",
                    "Check all dates, skills, accomplishments, and contact details before using the resume.")
    resume_text = resume_to_display_text(rewritten)
    with st.container(border=True):
        st.text_area("Generated resume content", value=resume_text, height=300, disabled=True)
        st.download_button(
            "⬇️ Download resume content (.txt)",
            data=resume_text,
            file_name="tailored_resume.txt",
            mime="text/plain",
            use_container_width=True,
        )

    section_heading("Step 03 · Design", "Create your formatted resume",
                    "Generate an HTML version that you can preview in the app and save locally.")
    if st.button("🎨 Generate HTML resume", type="primary", use_container_width=True):
        try:
            with st.spinner("Formatting your resume with Gemini..."):
                html_resume = format_resume_chain(rewritten)
            if not isinstance(html_resume, str) or not html_resume.strip():
                st.error("The formatter returned an empty result.")
            else:
                st.session_state.html_resume = html_resume
                st.rerun()
        except Exception as exc:
            st.error(f"Unable to format the resume: {exc}")

    html_resume = st.session_state.html_resume
    if html_resume:
        st.markdown('<div class="eyebrow">Preview</div>', unsafe_allow_html=True)
        st.subheader("Your formatted resume")
        st.components.v1.html(html_resume, height=1000, scrolling=True)

        safe_role = "".join(
            char if char.isalnum() else "_"
            for char in (st.session_state.resume_job_role or "tailored")
        ).strip("_")
        st.download_button(
            "⬇️ Download formatted resume (.html)",
            data=html_resume,
            file_name=f"{safe_role or 'tailored'}_resume.html",
            mime="text/html",
            type="primary",
            use_container_width=True,
        )


def main():
    with st.sidebar:
        st.markdown("<div style='font-size:2rem'>✨</div>", unsafe_allow_html=True)
        st.markdown("# Resume Studio")
        st.caption("Your career, more clearly presented.")
        st.divider()

        upload_file = st.file_uploader(
            "Upload your resume", type=["pdf"],
            help="Choose a text-based PDF resume.",
        )
        if upload_file:
            st.caption(f"Selected: {upload_file.name}")
        st.divider()
        st.markdown("**Workspace**")
        section = st.radio("Choose a view", SECTIONS, label_visibility="collapsed")
        st.divider()

        if st.session_state.ats is not None:
            st.markdown("<span style='color:#b8f6dd;font-weight:700'>● Resume analyzed</span>", unsafe_allow_html=True)
            st.caption("Your results are saved for this session.")
        else:
            st.caption("Upload a resume to unlock your personalized workspace.")

    if not api_key or llm is None:
        hero("Welcome", "AI Resume Studio", "A polished workspace for resume insights, skill discovery, and interview practice.")
        st.error("Gemini API key not found. Add GEMINI_API_KEY=your_key to your .env file, then restart Streamlit.")
        st.stop()

    if upload_file and upload_file.name != st.session_state.source_file:
        try:
            with st.spinner("Reading your resume and building your profile..."):
                extracted_text = extract_pdf_text(upload_file)
                cleaned_text = clean_resume_text(extracted_text)
                if not cleaned_text:
                    st.error("No text could be extracted. Please try a text-based PDF.")
                    st.stop()
                st.session_state.resume_text = cleaned_text
                run_analysis(cleaned_text, llm)
                st.session_state.source_file = upload_file.name
                st.session_state.current_question = None
                st.session_state.latest_evaluation = None
                st.session_state.rewritten_resume = None
                st.session_state.html_resume = None
                st.toast("Resume analysis is ready", icon="✅")
        except Exception as exc:
            st.session_state.source_file = None
            message = str(exc)
            if "429" in message or "RESOURCE_EXHAUSTED" in message:
                st.error("The Gemini API quota or rate limit has been reached. Check your project's quota and try again later.")
            elif "503" in message or "UNAVAILABLE" in message:
                st.error("Gemini is temporarily busy. Please wait and try again.")
            else:
                st.error("We couldn't finish analyzing this resume. Check the terminal for the full technical error.")
            st.exception(exc)
            st.stop()

    if st.session_state.ats is None:
        hero(
            "Welcome to your career workspace", "Make your resume work harder.",
            "Upload a PDF to get an ATS snapshot, discover your technical skills, practice interview questions, and tailor your resume to a role.",
        )
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        cards = [
            (col1, "📊 ATS analysis", "Understand strengths, gaps, keywords, and actionable improvements."),
            (col2, "🧠 Skills explorer", "See your technical toolkit grouped by category, with evidence."),
            (col3, "🎤 Mock interview", "Practice role-relevant questions and get structured feedback."),
            (col4, "✨ Resume Studio", "Tailor your content and export a formatted HTML resume."),
        ]
        for col, title, description in cards:
            with col:
                st.markdown(
                    f'<div class="panel"><div class="panel-title">{title}</div><div class="panel-caption">{description}</div></div>',
                    unsafe_allow_html=True,
                )
        st.info("Start by uploading your PDF in the sidebar.")
        st.markdown('<div class="footer-note">Built for thoughtful career preparation · Review AI-generated content before use.</div>', unsafe_allow_html=True)
        return

    if section == "ATS Analysis":
        render_ats(st.session_state.ats)
    elif section == "Skills Explorer":
        render_skills(st.session_state.skills)
    elif section == "Mock Interview":
        render_questions()
    elif section == "Resume Studio":
        render_resume_studio()

    st.markdown(
        '<div class="footer-note">AI-generated guidance · Keep your resume accurate to your real experience.</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()





# import streamlit as st
# from langchain_google_genai import ChatGoogleGenerativeAI
# from services.pdf_parser import extract_pdf_text
# from services.resume_extractor import clean_resume_text
# import os
# from dotenv import load_dotenv
# from chains.ats_chain import analyze_resume
# from chains.skill_chain import extract_skills_from_resume_chain
# from chains.interview_chain import generate_question_chain
# from chains.evaluation_chain import evaluate_answer_chain, EvaluationResult
# from chains.rewrite_chain import rewrite_resume_chain
# from chains.format_chain import format_resume_chain

# load_dotenv()
# os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
# llm = ChatGoogleGenerativeAI(
#     model="gemini-3.5-flash",
#     temperature=0.2,
# )

# SECTIONS = ["ATS Analysis", "Skills", "Interview Preparation"]
# for key in ("resume_text", "ats", "skills", "source_file", "current_question", "latest_evaluation", "rewritten_resume", "html_resume"):
#     st.session_state.setdefault(key, None)

# for key in ("questions", "answers", "evaluations"):
#     st.session_state.setdefault(key, [])

# if("total_score" not in st.session_state):
#     st.session_state.total_score = 0


# def run_analysis(cleaned_text, llm):
#     # Run ATS analysis
#     ats_response = analyze_resume(cleaned_text, llm)

#     # Build and execute the skills extraction chain
#     skills_chain = extract_skills_from_resume_chain(cleaned_text, llm)
#     skills_response = skills_chain.invoke({})

#     # Save results in Streamlit session state
#     st.session_state.ats = ats_response
#     st.session_state.skills = skills_response

#     return ats_response, skills_response


# def render_ats(ats_response):
#     st.success("Resume analysis completed!")
#     st.metric("ATS Score", ats_response.ats_score)

#     st.subheader("Strengths")
#     for strength in ats_response.strengths:
#         st.write(f"- {strength}")

#     st.subheader("Weaknesses")
#     for weakness in ats_response.weaknesses:
#         st.write(f"- {weakness}")

#     st.subheader("Missing Keywords")
#     for keyword in ats_response.missing_keywords:
#         st.write(f"- {keyword}")

#     st.subheader("Improvements")
#     for improvement in ats_response.improvements:
#         st.write(f"- {improvement}")

#     st.subheader("Summary")
#     st.write(ats_response.summary)


# def render_skills(skills_result):
#     st.header("Skills Overview")

#     if skills_result.candidate_name:
#         st.markdown(f"**Candidate:** {skills_result.candidate_name}")
#     if skills_result.target_role:
#         st.markdown(f"**Target Role:** {skills_result.target_role}")

#     st.subheader("Profile Summary")
#     st.write(skills_result.extraction_summary)

#     st.subheader("Skills by Category")
#     skill_groups = {
#         "Programming Languages": skills_result.skills.programming_languages,
#         "Frameworks & Libraries": skills_result.skills.frameworks_and_libraries,
#         "Databases": skills_result.skills.databases,
#         "Cloud & DevOps": skills_result.skills.cloud_and_devops,
#         "Tools & Platforms": skills_result.skills.tools_and_platforms,
#         "AI & ML": skills_result.skills.ai_and_ml,
#         "Domains & Concepts": skills_result.skills.domains_and_concepts,
#         "APIs & Protocols": skills_result.skills.apis_and_protocols,
#     }
#     for group_name, items in skill_groups.items():
#         if not items:
#             continue
#         with st.expander(f"{group_name} ({len(items)})"):
#             for skill in items:
#                 st.markdown(
#                     f"- **{skill.name}** — "
#                     f"`{skill.confidence.value}` · `{skill.proficiency_signal.value}`  \n"
#                     f"  _{skill.evidence}_"
#                 )

#     if skills_result.interview_focus_areas:
#         st.subheader("Interview Focus Areas")
#         for focus in skills_result.interview_focus_areas:
#             st.markdown(
#                 f"🎯 **{focus.skill}** (`{focus.suggested_depth.value}`)  \n"
#                 f"{focus.reason}"
#             )

#     if skills_result.skills_flat_list:
#         st.subheader("All Skills")
#         st.markdown(" ".join(f"`{s}`" for s in skills_result.skills_flat_list))


# def render_questions():
#     st.header("Mock Interview")
#     render_progress_metric()
#     st.divider()

#     if st.button("Start Mock Interview"):
#         st.session_state.questions = []
#         st.session_state.answers = []
#         st.session_state.evaluations = []
#         st.session_state.total_score = 0

#         question = generate_question_chain(
#             name=st.session_state.skills.candidate_name or "Candidate",
#             role=st.session_state.skills.target_role or "Target Role",
#             skills=st.session_state.skills.skills_flat_list,
#             previous_questions=st.session_state.questions,
#             llm=llm
#         ).invoke({})

#         st.session_state.current_question = question
#         st.session_state.questions.append(question.question)

#     if st.session_state.current_question:
#         ques = st.session_state.current_question
#         st.subheader("Interview Question")
#         st.info(question.question)

#         answer = st.text_area("Submit Your Answer", key="answer_input")

#         if st.button("Submit Your Answer"):
#             evaluation = evaluate_answer_chain(question=ques.question, 
#                                                answer=answer, 
#                                                difficulty=ques.difficulty, 
#                                                llm=llm
#                                                ).invoke({})

#             st.session_state.answers.append(answer)
#             st.session_state.evaluations.append(evaluation)
#             st.session_state.total_score += evaluation.overall_score
            
#             if not answer.strip():
#                 st.warning("Please enter your answer before submitting.")
#                 return

#             next_question = generate_question_chain(
#                 name=st.session_state.skills.candidate_name or "Candidate",
#                 role=st.session_state.skills.target_role or "Target Role",
#                 skills=st.session_state.skills.skills_flat_list,
#                 previous_questions=st.session_state.questions,
#                 llm=llm
#             ).invoke({})

#             st.session_state.current_question = next_question
#             st.session_state.questions.append(next_question.question)
#             st.session_state.latest_evaluation = evaluation
            
#             st.rerun()

#     if(st.session_state.latest_evaluation):
#         render_result(st.session_state.latest_evaluation)

#     render_questions_history()
    

# def render_progress_metric():
#     completed = len(st.session_state.answers)
#     avg_score = (st.session_state.total_score / completed) if completed > 0 else 0

#     col1, col2, col3 = st.columns(3)
#     with col1:
#         col1.metric("Questions Completed", completed)
    
#     with col2:
#         col2.metric("Average Score", round(avg_score, 1))
    
#     with col3:
#         col3.metric("Total Score", st.session_state.total_score)

#     progress = min(completed/10, 1.0)
#     st.progress(progress)


# def render_result(evaluation):
#     st.divider()
#     st.subheader("Evaluation Results")
#     col1, col2, col3 = st.columns(3)

#     with col1:
#         st.metric("Overall", f"{evaluation.overall_score}")

#     with col2:
#         st.metric("Technical Accuracy", f"{evaluation.technical_accuracy}/10")

#     with col3:
#         st.metric("Clarity", f"{evaluation.clarity}/10")

#     st.write("### Strengths")
#     for item in evaluation.strengths:
#         st.write(f"- {item}")

#     st.write("### Weaknesses")
#     for item in evaluation.weaknesses:
#         st.write(f"- {item}")

#     st.write("### Improvements")
#     for item in evaluation.improvements:
#         st.write(f"- {item}")

#     st.write("### Ideal Answer")
#     st.info(evaluation.ideal_answer)


# def render_questions_history():
#     with st.expander("Interview History"):
#         for i, (q, a, e) in enumerate(zip(st.session_state.questions,
#                                           st.session_state.answers,
#                                           st.session_state.evaluations                            
#         )):
#             st.write(f"### Question {i+1}")
#             st.write(q.question)
#             st.write("***Your Answer***")
#             st.write(a)
#             st.write(f"Score: {e.overall_score}/10")
#             st.divider()

# def render_rewrite_resume():
#     job_role = st.text_input("Enter Job Role")
#     job_description = st.text_area("Enter Job Description")

#     if st.button("Rewite Resume"):
#         if(job_role and job_description):
#             rewritten_resume = rewrite_resume_chain(
#                 resume = st.session_state.resume_text,
#                 ats = st.session_state.ats,
#                 skills = st.session_state.skills.skills_flat_list,
#                 job_role = job_role,
#                 job_description = job_description,
#                 llm = llm
#             ).invoke({})
#             st.session_state.rewritten_resume = rewritten_resume
#             st.session_state.html_resume = None
 
#         else:
#             st.warning("Please fill in both the fileds")
#     else:
#         if st.session_state.rewritten_resume:
#             st.markdown(st.session_state.rewritten_resume)

#             if st.button("Format Resume"):
#                 html_resume = format_resume_chain(st.session_state.rewritten_resume)
#                 st.session_state.html_resuem = html_resume

#         if st.session_state.get("html_resume"):
#             st.components.v1.html(st.session_state.html_resume, height=1100, scrolling=True)
#             st.download_button(
#                 label = "Download Resume (.html)",
#                 data = st.session_state.htmlresume,
#                 file_name = f"{st.session_state.rewritten_resume.contact.name.replace(' ', '_')}_resume.html",
#                 mime = "text/html"
#             )

# def main():
#     st.set_page_config(
#         page_title="AI Resume Analyzer & Interview Agent",
#         layout="wide"
#     )
    
#     with st.sidebar:
#         st.title("AI Resume Analyzer & Interview Agent")

#         upload_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"])
#         if(upload_file and upload_file.name != st.session_state.source_file):
#             with st.spinner("Extracting text from the uploaded PDF..."):
#                 extracted_text = extract_pdf_text(upload_file)
#                 cleaned_text = clean_resume_text(extracted_text)

#                 if (not cleaned_text):
#                     st.error("No text could be extracted from the uploaded PDF. Please ensure the file is a valid PDF and try again.")
#                     st.stop()
#                 st.toast("PDF Uploaded successfully!")

#             st.session_state.resume_text = cleaned_text
#             st.session_state.source_file = upload_file.name

#             with st.spinner("Analyzing your resume..."):
#                 run_analysis(cleaned_text, llm)
#             st.success("Resume analysis completed! You can now view the results in the selected section.")

#         section = st.radio("Select a section to view", SECTIONS, disabled=st.session_state is None)

#     if (st.session_state.ats is None):
#         st.title("AI RESUME ATS ANALYSER & INTERVIEW AGENT")
#         st.info("Please upload your resume in PDF format to begin the analysis.")
#         return

#     if (section == "ATS Analysis"):
#         render_ats(st.session_state.ats)
#     elif (section == "Skills"):
#         render_skills(st.session_state.skills)
#     elif (section == "Interview Preparation"):
#         render_questions()
#     elif (section == "Rewrite Resume"):
#         render_rewrite_resume()


#             # with st.spinner("Extracting skills from your resume..."):
#             #     skills_response = extract_skills_from_resume_chain(cleaned_text, llm)
#             #     st.session_state.skills = skills_response

# if __name__ == "__main__":
#     main()