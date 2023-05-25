import os
import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from common import find_in_list
from mindnode import Mindnode

HOME_PATH = os.environ["HOME"]
CACHE_PATH = os.environ["XDG_CACHE_HOME"]
MINDNODE_FILE = (
    f"{HOME_PATH}/Library/Mobile"
    " Documents/W6L39UYL6Z~com~mindnode~MindNode/Documents/Swarm Engine.mindnode"
)
MINDMAP_NAME = "Swarm Engine"
TOKEN_FILE = f"{CACHE_PATH}/google-api/token.pickle"
CREDENTIALS_FILE = f"{CACHE_PATH}/google-api/credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1COKPuQbeuAH3qk-ezEb0CE4V6YgoDdejCM1v3FimBCU"

mindnode = Mindnode(MINDNODE_FILE)

mind_map = find_in_list(mindnode.mind_maps, lambda m: m.title == "Swarm Engine")

service = None


def authenticate():
    global service

    token_path = Path(TOKEN_FILE)
    token_path.parent.mkdir(parents=True, exist_ok=True)
    credentials_path = Path(CREDENTIALS_FILE)
    credentials_path.parent.mkdir(parents=True, exist_ok=True)
    credentials_path.touch()

    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    service = build("sheets", "v4", credentials=creds)


def mind_map_to_2d_array(root_node):

    result = []

    for node in root_node.sub_nodes:

        lines = []

        if node.sub_nodes:
            sub_result = mind_map_to_2d_array(node)

            for line in sub_result:
                lines.append([node.title] + line)

        else:
            line = [node.title]

            line.append(node.hours / 24 or "")

            if node.done is not None:
                line.append("✅" if node.done else "")

            lines.append(line)

        result += lines

    return result


mind_map_array = mind_map_to_2d_array(mind_map)

compressed_array = [
    [line[0], " - ".join(line[1:-2]), line[-2], line[-1]] for line in mind_map_array
]

data = [["Category", "Task", "Est. Time", "Done"]] + compressed_array

authenticate()
service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID,
    range="Tasks!A1",
    valueInputOption="RAW",
    body=dict(
        majorDimension="ROWS",
        values=data,
    ),
).execute()

print(f"Updated {len(data)} lines")
