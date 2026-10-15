import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.prompt_reader import get_format_prompt

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-3.7-flash"),
    google_api_key=api_key,
    temperature=0,
    max_output_tokens=8192,
)


def format_resume_chain(resume):
    system_prompt = get_format_prompt()
    resume_json = resume.model_dump_json(indent=2)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=(
                "Generate a complete, well-formatted HTML resume "
                "using the following data. Return only HTML, without "
                "Markdown code fences.\n\n"
                f"{resume_json}"
            )
        ),
    ]

    response = llm.invoke(messages)
    html_output = response.content

    # Handle string or structured response content
    if not isinstance(html_output, str):
        if isinstance(html_output, list):
            html_output = "".join(
                block.get("text", "")
                for block in html_output
                if isinstance(block, dict)
            )
        else:
            html_output = str(html_output)

    # Remove Markdown fences if the model returns them
    html_output = html_output.strip()

    if html_output.startswith("```html"):
        html_output = html_output[len("```html"):].strip()
    elif html_output.startswith("```"):
        html_output = html_output[len("```"):].strip()

    if html_output.endswith("```"):
        html_output = html_output[:-3].strip()

    # Keep the complete HTML document
    doctype_index = html_output.lower().find("<!doctype html>")
    if doctype_index != -1:
        html_output = html_output[doctype_index:]

    return html_output