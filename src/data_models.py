from pydantic import BaseModel
from typing import Optional, List

class Story(BaseModel):
    story_id : str

class Subtask(BaseModel):
    subtask : str
    estimation : int

class StoryDesc(BaseModel):
    status : int
    story_id : str
    description : Optional[str] = None

class StoryEstimate(BaseModel):
    status : int
    story_id : str
    description : Optional[str] = None
    subtasks : Optional[List] = None