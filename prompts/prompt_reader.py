import os

PROMPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_ats_prompt():
    prompt_path = os.path.join(PROMPT_DIR, "ats_prompt.md")
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()

def get_skills_prompt():
    prompt_path = os.path.join(PROMPT_DIR, "skills_prompt.md")
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()

def get_interview_prompt():
    prompt_path = os.path.join(PROMPT_DIR, "interview_prompt.md")
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()

def get_evaluation_prompt():
    prompt_path = os.path.join(PROMPT_DIR, "evaluation_prompt.md")
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()
