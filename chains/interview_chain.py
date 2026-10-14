from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from prompts.prompt_reader import get_interview_prompt

class Difficulty(str, Enum):
    EASY   = "EASY"
    MEDIUM = "MEDIUM"
    HARD   = "HARD"

class InterviewQuestion(BaseModel):
    question: str = Field(..., description="The interview question")
    difficulty: Difficulty = Field(..., description="Difficulty level of the question")
    context: Optional[str] = Field(None, description="Additional context or information for the question")


def create_context(name, role, skills, previous_questions):
    return f"""
    System Prompt : {get_interview_prompt()}
    Name : {name}
    Role : {role}
    Skills : {skills}
    Previous Questions : {previous_questions}
    """

def generate_question_chain(name: str, role: str, skills: List[str], previous_questions: List[InterviewQuestion], llm):
    context = create_context(name, role, skills, previous_questions)
    prompt = ChatPromptTemplate.from_messages([("human", context)])
    structured_llm = llm.with_structured_output(InterviewQuestion)
    chain = prompt | structured_llm

    return chain