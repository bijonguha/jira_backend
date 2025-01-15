import json
from tqdm import tqdm
from typing import Optional, List, Dict
from pydantic import BaseModel

from datetime import datetime, timedelta, timezone

# Helper function to parse the datetime string
def parse_datetime(date_str):

    if type(date_str) == datetime:
        return date_str
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")

class Author(BaseModel):
    self: Optional[str] = None
    accountId: Optional[str] = None
    emailAddress: Optional[str] = None
    displayName: Optional[str] = None
    active: Optional[bool] = None
    timeZone: Optional[str] = None
    accountType: Optional[str] = None

class ChangelogItem(BaseModel):
    field: Optional[str] = None
    fieldtype: Optional[str] = None
    fieldId: Optional[str] = None
    from_: Optional[str] = None
    fromString: Optional[str] = None
    to: Optional[str] = None
    toString: Optional[str] = None

class History(BaseModel):
    id: Optional[str] = None
    author: Optional[Author] = None
    created: Optional[str] = None
    items: Optional[List[ChangelogItem]] = None

class Changelog(BaseModel):
    startAt: Optional[int] = None
    maxResults: Optional[int] = None
    total: Optional[int] = None
    histories: Optional[List[History]] = None

class Priority(BaseModel):
    self: Optional[str] = None
    iconUrl: Optional[str] = None
    name: Optional[str] = None
    id: Optional[str] = None

class StatusCategory(BaseModel):
    self: Optional[str] = None
    id: Optional[int] = None
    key: Optional[str] = None
    colorName: Optional[str] = None
    name: Optional[str] = None

class Status(BaseModel):
    self: Optional[str] = None
    description: Optional[str] = None
    iconUrl: Optional[str] = None
    name: Optional[str] = None
    id: Optional[str] = None
    statusCategory: Optional[StatusCategory] = None

class Fields(BaseModel):
    summary: Optional[str] = None
    resolutiondate: Optional[str] = None
    created: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    customfield_10110: Optional[float] = None

class JiraIssue(BaseModel):
    expand: Optional[str] = None
    id: Optional[str] = None
    self: Optional[str] = None
    key: Optional[str] = None
    changelog: Optional[Changelog] = None
    fields: Optional[Fields] = None

class JiraData(BaseModel):
    issues: Optional[Dict[str, JiraIssue]] = None

filepath = r"D:\@Genai_kt\@JIRA_estimator\react-hello-world\jira_fstack_app\src\dataprocessing\TMA.json"

with open(filepath, "r") as f:
    jira_dump = json.load(f)
    print("Loaded JSON data from file")

print(jira_dump.keys())

jira_dump_models = {}

for key in tqdm(jira_dump.keys(), desc="Processing Jira issues"):

    try:
        jira_dump_models[key] = JiraIssue(**jira_dump[key])
    except Exception as e:
        print(f"Error processing {key}: {str(e)}")
        continue

def filter_hist_status(history_list: List[History]) -> str:

    hist_status = []
    for hist in history_list:
        for item in hist.items:
            if item.field == "status":
                hist_status.append(hist)

        if len(hist_status) > 0:
            hist.created = parse_datetime(hist.created)
                
    return hist_status

def filter_timespent_status(history_list: List[History]) -> str:

    hist_status = []
    for hist in history_list:
        for item in hist.items:
            if item.field == "timespent":
                hist_status.append(hist)

        if len(hist_status) > 0:
            hist.created = parse_datetime(hist.created)
                
    return hist_status

def filter_timeestimate_status(history_list: List[History]) -> str:

    hist_status = []
    for hist in history_list:
        for item in hist.items:
            if item.field == "timeestimate":
                hist_status.append(hist)

        if len(hist_status) > 0:
            hist.created = parse_datetime(hist.created)
                
    return hist_status

def filter_hist_items_timeestimate(change_items_list : ChangelogItem):

    new_item_list = []

    for item in change_items_list:
        if item.field == "timeestimate":
            new_item_list.append(item)
    
    return new_item_list

def filter_hist_items_status(change_items_list : ChangelogItem):

    new_item_list = []

    for item in change_items_list:
        if item.field == "status":
            new_item_list.append(item)
    
    return new_item_list

def filter_hist_items_status_blocked(change_items_list : ChangelogItem):

    new_item_list = []

    for item in change_items_list:
        if item.field == "status" and item.toString == "Blocked":
            new_item_list.append(item)
        if item.field == "status" and item.fromString == "Blocked":
            new_item_list.append(item)
    
    return new_item_list

def count_weekdays(start_date, end_date):
    day_count = 0
    current_date = start_date
    while current_date <= end_date:
        # Exclude Saturday (5) and Sunday (6)
        if current_date.weekday() < 5:
            day_count += 1
        current_date += timedelta(days=1)
    return day_count
    
def count_in_progress_efforts(hist_items) -> int:

    print("In Progress Efforts")
    effort_count = 0
    q_prog = []
    q_pro_datetime = {}
    tmp_effort_dict = {}

    for index,hist in enumerate(hist_items):
        if hist.items[0].toString == "In Progress":
            q_prog.append(index)
            tmp_effort_dict["started_at"] = hist.created
            

        elif hist.items[0].fromString == "In Progress" and len(q_prog) > 0:
            effort_count += 1
            q_prog.pop(0)
            tmp_effort_dict["ended_at"] = hist.created
            q_pro_datetime["inP2D-{}".format(effort_count)] = tmp_effort_dict
            tmp_effort_dict = {}
            

    total_efforts = 0

    for key, value in q_pro_datetime.items():
        # Ensure both start and end dates are present
        if 'started_at' in value and 'ended_at' in value:
            total_efforts_diff = count_weekdays(value["started_at"], value["ended_at"])
            total_efforts += total_efforts_diff
            print(f"Effort {key} : {total_efforts_diff}")

    q_pro_datetime["total_efforts"] = total_efforts
    print(q_pro_datetime)
    return q_pro_datetime, total_efforts

def count_in_blocked_efforts(hist_items) -> int:

    print("Blocked Efforts")
    effort_count = 0
    q_prog = []
    q_pro_datetime = {}
    tmp_effort_dict = {}

    for index,hist in enumerate(hist_items):
        if hist.items[0].toString == "Blocked":
            q_prog.append(index)
            tmp_effort_dict["started_at"] = hist.created
            

        elif hist.items[0].fromString == "Blocked" and len(q_prog) > 0:
            effort_count += 1
            q_prog.pop(0)
            tmp_effort_dict["ended_at"] = hist.created
            q_pro_datetime["BLKD-{}".format(effort_count)] = tmp_effort_dict
            tmp_effort_dict = {}
            

    total_efforts = 0

    for key, value in q_pro_datetime.items():
        # Ensure both start and end dates are present
        if 'started_at' in value and 'ended_at' in value:
            total_efforts_diff = count_weekdays(value["started_at"], value["ended_at"])
            total_efforts += total_efforts_diff
            print(f"Effort {key} : {total_efforts_diff}")

    q_pro_datetime["total_efforts"] = total_efforts
    print(q_pro_datetime)
    return q_pro_datetime, total_efforts

def count_ready_for_testing_efforts(hist_items) -> int:

    print("Ready for Testing Efforts")
    effort_count = 0
    q_prog = []
    q_pro_datetime = {}
    tmp_effort_dict = {}

    for index,hist in enumerate(hist_items):
        if hist.items[0].toString == "Ready for Testing":
            q_prog.append(index)
            tmp_effort_dict["started_at"] = hist.created
            

        elif hist.items[0].fromString == "Ready for Testing" and len(q_prog) > 0:
            effort_count += 1
            q_prog.pop(0)
            tmp_effort_dict["ended_at"] = hist.created
            q_pro_datetime["inR2T-{}".format(effort_count)] = tmp_effort_dict
            tmp_effort_dict = {}
            

    total_efforts = 0

    for key, value in q_pro_datetime.items():
        # Ensure both start and end dates are present
        if 'started_at' in value and 'ended_at' in value:
            total_efforts_diff = count_weekdays(value["started_at"], value["ended_at"])
            total_efforts += total_efforts_diff
            print(f"Effort {key} : {total_efforts_diff}")

    q_pro_datetime["total_efforts"] = total_efforts
    print(q_pro_datetime)
    return q_pro_datetime, total_efforts

def count_in_testing_efforts(hist_items) -> int:

    print("In Testing Efforts")
    effort_count = 0
    q_prog = []
    q_pro_datetime = {}
    tmp_effort_dict = {}

    for index,hist in enumerate(hist_items):
        if hist.items[0].toString == "In Testing":
            q_prog.append(index)
            tmp_effort_dict["started_at"] = hist.created
            

        elif hist.items[0].fromString == "In Testing" and len(q_prog) > 0:
            effort_count += 1
            q_prog.pop(0)
            tmp_effort_dict["ended_at"] = hist.created
            q_pro_datetime["inTST-{}".format(effort_count)] = tmp_effort_dict
            tmp_effort_dict = {}
            

    total_efforts = 0

    for key, value in q_pro_datetime.items():
        # Ensure both start and end dates are present
        if 'started_at' in value and 'ended_at' in value:
            total_efforts_diff = count_weekdays(value["started_at"], value["ended_at"])
            total_efforts += total_efforts_diff
            print(f"Effort {key} : {total_efforts_diff}")

    q_pro_datetime["total_efforts"] = total_efforts
    print(q_pro_datetime)
    return q_pro_datetime, total_efforts

df_dict_all = []

for issue_key, issue in tqdm(jira_dump_models.items(), desc="Filtering Jira issues"):

    df_dict = {}
    # story_key,story_summary,story_description,status,story_points,story_priority,story_created_date,story_resolved_date
    df_dict["story_key"] = issue_key
    df_dict["story_summary"] = issue.fields.summary
    df_dict["story_description"] = issue.fields.description
    df_dict["status"] = issue.fields.status.name
    df_dict["story_points"] = issue.fields.customfield_10110
    df_dict["story_priority"] = issue.fields.priority.name

    # if issue_key == "PP24-7107":
    #     print("+-+"*100)
    # else:
    #     continue
    
    hist_status_timeestimate = filter_timeestimate_status(issue.changelog.histories)
    sorted_timeestimate_list = sorted(hist_status_timeestimate, key=lambda x: x.created)


    if len(sorted_timeestimate_list) > 0:
        tes_hist = sorted_timeestimate_list[-1]
        ts = filter_hist_items_timeestimate(sorted_timeestimate_list[-1].items)
        print(f"***ID***: {tes_hist.id}, ***Timeestimate Created***: {tes_hist.created}, \
            **FROM**: {ts[0].fromString} **TO** : {ts[0].toString}\n")
        
        total_toestimated_time = int(ts[0].toString)/3600 if ts[0].toString else 0

    hist_status_issues = filter_hist_status(issue.changelog.histories)
    sorted_history_list = sorted(hist_status_issues, key=lambda x: x.created)
    issue.changelog.histories = sorted_history_list

    print(jira_dump_models[issue_key].changelog.histories)

    # Printing the sorted list to verify
    for history in sorted_history_list:
        history.items = filter_hist_items_status(history.items)
        print(f"***ID***: {history.id}, ***Created***: {history.created}, \
              **FROM**: {history.items[0].fromString} **TO** : {history.items[0].toString}\n")

    print("Issue Key: ", issue_key)
    _, tip = count_in_progress_efforts(sorted_history_list)

    _, tib = count_in_blocked_efforts(sorted_history_list)

    _, trft = count_ready_for_testing_efforts(sorted_history_list)
    
    _, tite = count_in_testing_efforts(sorted_history_list)
    
    df_dict["total_in_progress_time"] = tip
    df_dict["total_blocked_time"] = tib
    df_dict["total_ready_for_testing_time"] = trft
    df_dict["total_in_testing_time"] = tite

    df_dict_all.append(df_dict)

    # for history in sorted_history_list:
    #     blocked_list_items = filter_hist_items_status_blocked(history.items)
    #     if len(blocked_list_items) > 0:
    #         print("="*5 + "\n"+str(blocked_list_items))

import pandas as pd

df = pd.DataFrame(df_dict_all)
df.to_csv("jira_stories_trial.csv", index=False)

