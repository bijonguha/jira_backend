import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
import yaml
from yaml.loader import SafeLoader
import json

with open("jira_config.yaml") as f:
    app_config = yaml.load(f, Loader=SafeLoader)

# Jira API credentials
username = app_config["username"]
api_token = app_config["api_token"]
jira_url = app_config["jira_url"]
project_name = app_config["project_name"]
jql = app_config['jira_query']

start_at = 0
all_Stories_dict = {}
max_results = 1000
count = 0

while True:
    # API request
    response = requests.get(f'{jira_url}/rest/api/2/search',
                            params={
                                'jql': jql,
                                'startAt': start_at,
                                'maxResults': max_results,
                                'fields': 'key,summary,description,status,customfield_10110,priority,created,resolutiondate',
                                'expand': 'changelog'
                            },
                            auth=HTTPBasicAuth(username, api_token))
    
    # Check for successful response
    if response.status_code != 200:
        print(f'Failed to fetch data: {response.status_code} - {response.text}')
        break
    
    data = response.json()
    issues = data['issues']
    
    # Append issues to all_stories list
    for issue in issues:
        
        print(f'Processing story: {issue["key"]}')
        
        all_Stories_dict[issue['key']] = issue

    count += 1

    # Break the loop if no more issues are returned
    if count < max_results:
        break


with open(f"{project_name}.json", "w") as f:
    json.dump(all_Stories_dict, f)

