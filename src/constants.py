import os
from enum import Enum

class Constants(Enum):

    CONFIG_APP = (
        os.path.join("config", "app.prod.yaml")
        if os.getenv("APP_ENV") == "PROD"
        else os.path.join("config", "app.dev.yaml")
    )

    PROMPT_PATH = os.path.join("config", "prompt_v1.txt")
    