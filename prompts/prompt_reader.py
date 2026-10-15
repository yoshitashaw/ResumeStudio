from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent

def get_ats_prompt():
    prompt_path = PROMPTS_DIR / "ats_prompt.md"
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()

def get_skills_prompt():
    prompt_path = PROMPTS_DIR / "skills_prompt.md"
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()

def get_interview_prompt():
    prompt_path = PROMPTS_DIR / "interview_prompt.md"
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()

def get_evaluation_prompt():
    prompt_path = PROMPTS_DIR / "evaluation_prompt.md"
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()

def get_rewrite_prompt():
    prompt_path = PROMPTS_DIR / "rewrite_prompt.md"
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()


def get_format_prompt():
    prompt_path = PROMPTS_DIR / "format_prompt.md"
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()



# import os

# PROMPT_DIR = os.path.dirname(os.path.abspath(__file__))

# def get_ats_prompt():
#     prompt_path = os.path.join(PROMPT_DIR, "ats_prompt.md")
#     with open(prompt_path, "r", encoding="utf-8") as file:
#         return file.read()

# def get_skills_prompt():
#     prompt_path = os.path.join(PROMPT_DIR, "skills_prompt.md")
#     with open(prompt_path, "r", encoding="utf-8") as file:
#         return file.read()

# def get_interview_prompt():
#     prompt_path = os.path.join(PROMPT_DIR, "interview_prompt.md")
#     with open(prompt_path, "r", encoding="utf-8") as file:
#         return file.read()

# def get_evaluation_prompt():
#     prompt_path = os.path.join(PROMPT_DIR, "evaluation_prompt.md")
#     with open(prompt_path, "r", encoding="utf-8") as file:
#         return file.read()

# def get_rewrite_prompt():
#     prompt_path = PROMPT_DIR / "rewrite_prompt.md"
#     with open(prompt_path, "r", encoding="utf-8") as file:
#         return file.read()

# def get_format_prompt():
#     prompt_path = PROMPT_DIR / "format_prompt.md"
#     with open(prompt_path, "r", encoding="utf-8") as file:
#         return file.read()

