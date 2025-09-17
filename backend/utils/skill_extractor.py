import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
import ast

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_skills_and_feedback_from_text(text: str) -> tuple[list[str], str]:
    prompt = (
        "Extract a comprehensive list of all relevant skills from this resume text, including technical skills, soft skills, and domain-specific skills. "
        "Return them as a Python list of strings labeled 'Skills'. Also provide feedback labeled 'Feedback' on how the resume can be improved. "
        "Ensure the response is structured as follows:\n\nSkills: [skill1, skill2, skill3]\nFeedback: Your feedback here\n\n" +
        "If skills are not explicitly listed, infer them from the text and provide them in the 'Skills' section. "
        "Ensure to include all types of skills, even if they are scattered throughout the text.\n\n" + text[:3000]
    )

    try:
        logger.debug("Prompt sent to OpenAI: %s", prompt)  # Log the prompt
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use a cheaper model
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500,
        )
        content = response.choices[0].message.content.strip()

        logger.debug("Raw OpenAI response: %s", content)  # Debugging log

        if "Feedback:" in content:
            try:
                skills_str, feedback = content.split("Feedback:", 1)
                logger.debug("Extracted skills string: %s", skills_str)  # Log extracted skills string
                logger.debug("Extracted feedback string: %s", feedback)  # Log extracted feedback string

                # Remove 'Skills:' prefix and sanitize
                skills_str = skills_str.replace("Skills:", "", 1).strip()
                skills_str = skills_str.strip("[]")  # Remove surrounding brackets if present

                # Parse Python literal safely
                try:
                    skills = ast.literal_eval(f"[{skills_str}]")
                    if not isinstance(skills, list):
                        raise ValueError("Parsed skills is not a list")
                except (ValueError, SyntaxError) as parse_error:
                    logger.error("Error parsing skills string: %s", parse_error)
                    skills = [skills_str]  # Fallback to raw skills string

                feedback = feedback.strip()
            except Exception as parse_error:
                logger.error("Error parsing response: %s", parse_error)
                skills = [skills_str]  # Fallback to raw skills string
                feedback = "Unable to parse feedback."
        else:
            logger.warning("Response does not contain 'Feedback:'")
            skills = []
            feedback = "Feedback not provided."

        return skills, feedback

    except Exception as e:
        logger.error("Error generating response: %s", e)
        return [], "Unable to generate feedback."
