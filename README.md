# ✨ ResumeStudio — AI-Powered Resume Analyzer

ResumeStudio is an AI-powered career preparation tool built with **Python, Streamlit, and Google Gemini**. It helps job seekers analyze their resumes, identify skill gaps, prepare for technical interviews, and generate job-specific resume versions through an interactive web application.

By combining ATS analysis, skill extraction, mock interviews, and AI-powered resume rewriting in one workspace, ResumeStudio helps candidates prepare more effectively for job applications.

## 🚀 Features

### 📊 ATS Resume Analysis
- Generate an ATS compatibility score for your resume.
- Identify resume strengths and weaknesses.
- Discover missing keywords relevant to improving your resume.
- Receive actionable suggestions to improve resume content and structure.
- Get an AI-generated summary of your resume.

### 🧠 Skills Explorer
- Extract technical skills and technologies from uploaded resumes.
- Organize skills into categories such as programming languages, frameworks, databases, cloud, DevOps, AI/ML, and tools.
- View confidence levels, proficiency signals, and supporting resume evidence.
- Identify important topics to focus on during interview preparation.

### 🎤 AI-Powered Mock Interviews
- Generate interview questions based on your resume and technical skills.
- Practice answering questions interactively.
- Receive AI-generated feedback on technical accuracy, clarity, strengths, and weaknesses.
- Get actionable improvement suggestions and example answers.
- Track scores and review previous interview attempts.

### 📝 Job-Specific Resume Rewriting
- Enter a target job role and its job description.
- Generate a tailored resume aligned with the opportunity.
- Improve professional summaries and experience bullet points.
- Highlight relevant skills, projects, and qualifications.
- Preserve the candidate's actual experience and qualifications rather than inventing credentials.

### 🎨 Resume Formatting & Export
- Transform structured resume data into a polished HTML resume.
- Preview the formatted resume directly in the application.
- Download the tailored resume content as a text file.
- Export the formatted resume as an HTML file.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core application logic and backend processing |
| **Streamlit** | Interactive web interface and application state management |
| **Google Gemini API** | ATS analysis, skill extraction, interview generation, answer evaluation, and resume rewriting |
| **LangChain** | Prompt management, LLM integration, and chain orchestration |
| **Pydantic** | Structured output schemas and response validation |
| **PyMuPDF** | Extracting text from uploaded PDF resumes |
| **python-dotenv** | Managing environment variables and API configuration |
| **HTML & CSS** | Custom interface styling and generated resume layouts |

## 🎥 ResumeStudio Demo
<img width="1906" height="877" alt="ResumeStudio SS" src="https://github.com/user-attachments/assets/03a89641-2467-4204-a471-622189d12aa4" />
Download Video: https://github.com/yoshitashaw/ResumeStudio/blob/master/ResumeStudio_Demo.mp4


## 🏗️ Project Structure

```text
ResumeStudio/
│
├── app.py
├── requirements.txt
├── .env
│
├── chains/
│   ├── ats_chain.py
│   ├── skill_chain.py
│   ├── interview_chain.py
│   ├── evaluation_chain.py
│   ├── rewrite_chain.py
│   └── format_chain.py
│
├── prompts/
│   ├── ats_prompt.md
│   ├── skills_prompt.md
│   ├── interview_prompt.md
│   ├── evaluation_prompt.md
│   ├── rewrite_prompt.md
│   ├── format_prompt.md
│   └── prompt_reader.py
│
└── services/
    ├── pdf_parser.py
    └── resume_extractor.py
```

## ⚙️ Getting Started

### Prerequisites

- Python 3.10 or later, compatible with your installed dependencies
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)
- Git

### 1. Clone the repository

```bash
git clone https://github.com/yoshitashaw/ResumeStudio.git
cd ResumeStudio
```

### 2. Create and activate a virtual environment

**Windows — PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
```

Use a model ID supported by your Google AI Studio project. Never commit your actual API key to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, typically `http://localhost:8501`.

## 📖 How to Use

1. **Upload your resume:** Select a PDF file from the sidebar.
2. **Analyze your resume:** Review your ATS score, strengths, weaknesses, and improvement suggestions.
3. **Explore your skills:** Examine extracted technologies and recommended interview focus areas.
4. **Practice interviews:** Generate questions, submit answers, and review your evaluation.
5. **Tailor your resume:** Enter a target job role and paste its job description.
6. **Format and export:** Preview the generated HTML resume and download it for further use.

## 🔐 Security & Privacy

- Store API keys in environment variables rather than source code.
- Keep `.env` and your virtual environment out of version control.
- Review AI-generated resume content carefully before submitting applications.
- Avoid uploading sensitive personal information unless you are comfortable processing it through the configured AI service.

## 🎯 Project Objective

ResumeStudio aims to bring resume optimization and interview preparation together in a single AI-powered workspace, helping candidates identify improvement areas, showcase relevant skills, and prepare for role-specific opportunities.

## 👩‍💻 Author

**Yoshita Shaw**

- GitHub: [@yoshitashaw](https://github.com/yoshitashaw)

---

*Built with Python, Streamlit, LangChain, and Google Gemini.*
