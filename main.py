from dotenv import load_dotenv
load_dotenv()

import yaml
from yaml.loader import SafeLoader

from typing import Annotated

from fastapi import FastAPI, Request, Header, Query
from fastapi.middleware.cors import CORSMiddleware

from src.data_models import Story, StoryDesc, StoryEstimate

from src.constants import Constants

from src.logger import setup_logger

from src.jira_handler import JiraHandler

LOGGER = setup_logger(__name__)

# Installed libraries
def get_app() -> FastAPI:
    """
    Returns the FastAPI app object
    """
    try:
        fast_app = FastAPI(
                title="GenAI Jira Estimator",
                description="A simple FastAPI backend for Mr. Agile application.")
        return fast_app
    except Exception as e:
        LOGGER.error('exception occured in get_app() - {0}'.format(e))

app = get_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["health"])
async def health_check(request: Request):
    """
    Health check endpoint
    """
    return {"status": 200}

@app.post("/story_id", tags=["Estimation"],
          summary="Estimate story subtasks with story id")
async def estimate_story(story_info: Story, username: Annotated[str, Header()],
                         api_token: Annotated[str, Header()], jira_url: Annotated[str, Header()],
                         prompt_template: Annotated[str | None, Query()] = None):
    """
    Story estimation endpoint
    """

    jira_handler = JiraHandler(username, api_token, jira_url)
    
    if not jira_handler.check_health():
        response = {
            "status": 400,
            "message": "Failed to connect to JIRA"
        }
        return response
    
    result = jira_handler.get_story_estimate(story_info.story_id, prompt_template)

    return StoryEstimate(**result)

@app.post("/create_subtasks", tags=["Estimation"],
          summary="Creation of subtasks in JIRA for the given story id")
async def create_subtasks_for_story(story_info: StoryEstimate, username: Annotated[str, Header()],
                         api_token: Annotated[str, Header()], jira_url: Annotated[str, Header()]):
    """
    Story estimation endpoint
    """
    jira_handler = JiraHandler(username, api_token, jira_url)

    if not jira_handler.check_health():
        response = {
            "status": 400,
            "message": "Failed to connect to JIRA"
        }
        return response

    response = jira_handler.create_tasks_from_estimate(story_info.dict())
    
    return response

