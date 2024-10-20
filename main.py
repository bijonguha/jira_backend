from dotenv import load_dotenv
load_dotenv()

import yaml
from yaml.loader import SafeLoader

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.data_models import Story, StoryDesc, StoryEstimate

from src.constants import Constants

from src.logger import setup_logger

from src.jira_handler import JiraHandler

LOGGER = setup_logger(__name__)

with open(Constants.CONFIG_APP.value) as f:
    app_config = yaml.load(f, Loader=SafeLoader)

jira_handler = JiraHandler(app_config["username"], app_config["api_token"], app_config["jira_url"])
assert jira_handler.check_health()

# Installed libraries
def get_app() -> FastAPI:
    """
    Returns the FastAPI app object
    """
    try:
        fast_app = FastAPI(
                title="Mr. Agile - Jira Estimator",
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
          summary="Estimate story subtasks with story id",
          response_model=StoryEstimate)
async def estimate_story(story_info: Story):
    """
    Story estimation endpoint
    """
    
    result = jira_handler.get_story_estimate(story_info.story_id)
    
    return StoryEstimate(**result)

@app.post("/create_subtasks", tags=["Estimation"],
          summary="Creation of subtasks in JIRA for the given story id")
async def create_subtasks_for_story(story_info: StoryEstimate):
    """
    Story estimation endpoint
    """

    response = jira_handler.create_tasks_from_estimate(story_info.dict())
    
    return response

