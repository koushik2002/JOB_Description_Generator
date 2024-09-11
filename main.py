from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
os.environ["API_KEY"] = "-------------------"

# Configure the Google Gemini API
genai.configure(api_key=os.environ["API_KEY"])

# Initialize FastAPI app
app = FastAPI()

# Define input data model
class JobDescriptionInput(BaseModel):
    job_title: str
    experience: str
    location: str
    education: str
    work_mode: str
    application_end_date: str
    job_start_date: str

# Define output data model
class JobDescriptionResponse(BaseModel):
    job_description: str
    roles_and_responsibilities: list
    required_skills: list
    status: bool

# Initialize the Gemini model with JSON output configuration
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

# Define a route for generating job descriptions
@app.post("/generate-job-description", response_model=JobDescriptionResponse)
async def generate_job_description_endpoint(input_data: JobDescriptionInput):
    try:
        # Create the prompt for the Gemini model
        prompt = f"""
        Create a job description for a {input_data.job_title} with {input_data.experience} experience in {input_data.location}.
        The candidate should have a degree in {input_data.education} and the job will be in {input_data.work_mode} mode.
        Applications close on {input_data.application_end_date}, and the job starts on {input_data.job_start_date}.
        Please provide the following details in JSON format:
        - job_description: str
        - roles_and_responsibilities: list[str]
        - required_skills: list[str]
        """
        
        # Generate job description using the Gemini model
        response = model.generate_content(prompt)
        
        # Parse the JSON response string into a Python dictionary
        generated_content = json.loads(response.text)
        
        # Structure the response
        job_description = {
            "job_description": generated_content.get("job_description", "Description not provided."),
            "roles_and_responsibilities": generated_content.get("roles_and_responsibilities", []),
            "required_skills": generated_content.get("required_skills", []),
            "status": True
        }

        return job_description

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while generating the job description: {str(e)}")
