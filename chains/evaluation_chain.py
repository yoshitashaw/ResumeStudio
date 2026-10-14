from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from prompts.prompt_reader import get_evaluation_prompt

class EvaluationResult(BaseModel):
    overall_score: int
    technical_accuracy: int
    clarity: int
    completeness: int
    strengths: List[str]
    weaknesses: List[str]
    improvements: List[str]
    ideal_answer: str

def create_context(question, answer, difficulty):
    return f"""
    System Prompt : {get_evaluation_prompt()}
    Question : {question}
    Answer : {answer}
    Difficulty : {difficulty}
    """

def evaluate_answer_chain(question: str, answer: str, difficulty: str, llm):
    context = create_context(question, answer, difficulty)
    prompt = ChatPromptTemplate.from_messages([("human", context)])
    structured_llm = llm.with_structured_output(EvaluateResponse)
    chain = prompt | structured_llm

    return chain