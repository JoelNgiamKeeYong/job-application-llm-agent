import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()


class Chain:


    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile"
        )     


    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )

        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={'page_data': cleaned_text})

        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]
    


    def write_email(self, job, portfolio):
        prompt_job_application = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION
            {job_description}

            ### INSTRUCTIONS  
            - Craft a **professional, personalized, and compelling** cover letter tailored to the given job description.  
            - Highlight **relevant skills, experiences, and achievements** that align with the role.  
            - Maintain a **confident, enthusiastic, and engaging** tone while keeping it formal yet approachable.  
            - Structure the letter with a **clear introduction, body, and conclusion** for readability and impact.  
            - If I lack a required skill, **do not fabricate experience**—instead, focus on **related strengths** and transferable expertise.  
            - Incorporate **relevant projects and certifications** from my portfolio **(only briefly and only if applicable)**: {portfolio}  
            - Include a link to my portfolio website: **[https://personal-jnky.web.app/]** (Do not provide any other links).  
            - End with a **strong closing statement**, reaffirming interest in the role and willingness to discuss further.  

            Best regards,  
            Joel
            ```
            """
        )

        chain_email = prompt_job_application | self.llm
        res = chain_email.invoke({"job_description": str(job), "portfolio": portfolio})
        return res.content


if __name__ == '__main__':
    print(os.getenv("GROQ_API_KEY"))