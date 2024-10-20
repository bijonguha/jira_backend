import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
import json
import yaml
from yaml.loader import SafeLoader
from grollm import OpenAI_Grollm

from src.logger import setup_logger
LOGGER = setup_logger(__name__)

from src.constants import Constants
ol = OpenAI_Grollm()

with open(Constants.PROMPT_PATH.value, 'r') as f:
    prompt_template = f.read()

with open(Constants.CONFIG_APP.value) as f:
    app_config = yaml.load(f, Loader=SafeLoader)

class JiraHandler:

    def __init__(self, username, api_token, jira_url):

        self.username = username
        self.api_token = api_token
        self.jira_url = jira_url

    def check_health(self):

        response = requests.get(f'{self.jira_url}/rest/api/2/field', auth=HTTPBasicAuth(self.username, self.api_token))

        if response.status_code == 200:
            LOGGER.info("Connected to JIRA")
            return True
        else:
            LOGGER.error("Failed to connect to JIRA")
            return False

    def get_story_info(self, story_id):
        """
        Fetches the summary and description of a Jira story by its ID.
        
        Args:
            story_id (str): The ID of the Jira story.
        
        Returns:
            dict: A dictionary containing the story's description.
        """
        try:
            url = f'{self.jira_url}/rest/api/2/issue/{story_id}'

            response = requests.get(url, auth=HTTPBasicAuth(self.username, self.api_token))

            if response.status_code == 200:
                issue_data = response.json()

                story_summary = issue_data['fields'].get('summary', '')
                story_description = issue_data['fields'].get('description', '')

                LOGGER.info(f"Fetched story info for {story_id}")

                return {
                    "status": 200,
                    "story_id": story_id,
                    "description": story_summary + story_description 
                }
            else:
                LOGGER.error(f"Failed to fetch story info for {story_id}, Status code: {response.status_code}")
                return {
                    "status": 400,
                    "story_id": story_id
                }
        
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"Error fetching story info: {e}")
            return {
                "status" : 500,
                "story_id": story_id
            }
        
    def get_story_estimate(self, story_id):

        story_dict = self.get_story_info(story_id)

        if story_dict["status"] == 200:

            prompt = prompt_template.replace("{STORY_QUERY}", story_dict["description"])
            LOGGER.debug(f"Prompt text : {prompt}")

            try:
                estimate = ol.send_prompt(prompt)
                story_dict["subtasks"] = eval(estimate)
                return story_dict
            
            except Exception as e:
                LOGGER.error(f"Error generating estimate: {e}")
                story_dict["status"] = 500
                return story_dict

    def create_subtask(self, story_id, subtask_summary, subtask_estimate):
        """
        Creates a subtask in Jira under the given story ID.
        
        Args:
            story_id (str): The ID of the parent story.
            subtask_summary (str): Summary of the subtask.
            subtask_estimate (int): Estimate (in minutes) for the subtask.
        
        Returns:
            dict: A dictionary containing the subtask creation status.
        """
        url = f"{self.jira_url}/rest/api/2/issue/"
        headers = {
            "Content-Type": "application/json"
        }



        # Payload for creating a subtask
        payload = {
            "fields": {
                "project": {
                    "key": app_config["project_key"]  # Replace with your Jira project key
                },
                "parent": {
                    "key": story_id
                },
                "summary": subtask_summary,
                "description": "Don't forget to do this too.",
                "issuetype": {
                    "id": "10325"
                },
                # "timetracking": {
                #     "originalEstimate": f"{subtask_estimate}m"  # Estimate in minutes
                # }
            }
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), auth=HTTPBasicAuth(self.username, self.api_token))

            if response.status_code == 201:
                LOGGER.info(f"Subtask '{subtask_summary}' created successfully under story {story_id}")
                return {"status": 201, "message": "Subtask created successfully"}
            else:
                LOGGER.error(f"Failed to create subtask '{subtask_summary}', Status code: {response.status_code}")
                return {"status": response.status_code, "message": "Failed to create subtask"}

        except requests.exceptions.RequestException as e:
            LOGGER.error(f"Error creating subtask '{subtask_summary}': {e}")
            return {"status": 500, "message": "An error occurred during subtask creation"}

    def create_tasks_from_estimate(self, story_estimate_dict):
        """
        Creates subtasks based on the AI-generated estimate and assigns them in Jira.
        
        Args:
            story_id (str): The ID of the Jira story.
        """
        story_estimate = story_estimate_dict
        story_id = story_estimate["story_id"]

        if story_estimate["status"] == 200 and len(story_estimate["subtasks"]) > 0:
            for subtask in story_estimate["subtasks"]:
                subtask_summary = subtask.get("subtask", "Unnamed Subtask")
                subtask_estimate = subtask.get("estimation", 0)  # Estimate in minutes
                
                # Create each subtask
                creation_status = self.create_subtask(story_id, subtask_summary, subtask_estimate)
                LOGGER.info(f"Subtask creation status: {creation_status}")
        else:
            LOGGER.error(f"Failed to create tasks from estimate for story {story_id}.")
            return {"status":500,
                "message": f"Tasks couldnot be created for story id: {story_id}"}

        return {"status":200,
                "message": f"Tasks created successfully for story id: {story_id}"}