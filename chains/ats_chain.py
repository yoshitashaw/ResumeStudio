from typing import List
from pydantic import BaseModel, Field
from prompts.prompt_reader import get_ats_prompt

class ATSResponse(BaseModel):
    ats_score: int = Field(description="ATS compatibility score from 0 to 100")
    strengths: List[str] = Field(description="Specific strengths found in the resume")
    weaknesses: List[str] = Field(description="Specific weaknesses or gaps in the resume")
    missing_keywords: List[str] = Field(description="Relevant job-related keywords missing from the resume")
    improvements: List[str] = Field(description="Actionable suggestions to improve the resume")
    summary: str = Field(description="Concise overall evaluation of the resume")

def create_context(resume_text: str) -> str:
    return f"""
{get_ats_prompt()}

IMPORTANT OUTPUT REQUIREMENTS:
- Return all six fields defined in the ATSResponse schema.
- Do not omit any field.
- ats_score must be an integer between 0 and 100.
- strengths, weaknesses, missing_keywords, and improvements
  must each be lists of strings.
- summary must be a non-empty string.
- Base your evaluation only on the resume content.
- Do not invent qualifications, skills, or experience.

RESUME TEXT:
{resume_text}
"""

def analyze_resume(resume_text: str, llm) -> ATSResponse:
    context = create_context(resume_text)

    structured_llm = llm.with_structured_output(
        ATSResponse,
        method="json_schema"
    )

    response = structured_llm.invoke(context)
    return response
