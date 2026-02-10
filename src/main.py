import os, json

from client import Client
from settings import Settings
from workspace import Workspace
from fileEditor import FileEditor

settings = Settings("settings.json")
workspace = Workspace(settings, settings.source)
file_editor = FileEditor(settings, workspace)

################################################ TOOLS

def replace_in_file(file_path:str, old:str, new:str) -> str:
    print(f"[TOOL] REPLACING in {file_path}")
    # Read old content
    content = file_editor.read_in_workspace_file(file_path)
    # Correct old content
    new_content = content.replace(old, new)
    # Check changes
    if new_content == content:     
        print(f"[TOOL] - NOT REPLACED")
        file_editor.write_in_fails(f"# NOT REPLACED \n##filename: {file_path}\n\n##old: \n\n{old} \n\n##new: \n\n{new}\n\n")
        return "NOT REPLACED"
    # Write changes
    file_editor.write_in_workspace_file(file_path, new_content)
    print(f"[TOOL] - REPLACED")
    file_editor.write_in_corrections(f"# REPLACED \n##filename: {file_path}\n\n##old: \n\n{old} \n\n##new: \n\n{new}\n\n")
    return "REPLACED"

def write_in_file(file_path:str, text:str) -> str:
    print(f"[TOOL] WRITING {file_path}")
    return file_editor.write_in_workspace_file(file_path, text)

def read_file(file_path:str) -> str:
    print(f"[TOOL] READING {file_path}")
    return file_editor.read_in_workspace_file(file_path)

################################################ CONNECTION

try:
    agents_json = json.load(open(f"agents_settings.json", "r"))
    job_json = json.load(open(f"jobs/{settings.job_name}.json", "r"))
except Exception as e:
    raise Exception(f"Invalid agents_settings, Exception: {str(e)}")

data_for_server = json.dumps({
    "model": settings.model,
    "agents": agents_json,
    "job": job_json
}).encode("utf-8")

client = Client()
client.connect()
resp = client.authenticate(data_for_server)
if resp is None:
    print(f"{resp}")
    exit()

while(resp):
    print(f"\r\n{resp.strip()}")
    data_json = json.loads(resp)
    print(f"[COMMAND] {data_json["command"]}")
    response = None
    if data_json["command"] == "replace_in_file":
        response = replace_in_file(
            data_json["file_path"], data_json["old"], data_json["new"]
        )
    elif data_json["command"] == "write_in_file":
        response = write_in_file(data_json["file_path"], data_json["text"])
    elif data_json["command"] == "list":
        response = workspace.files
    elif data_json["command"] == "read_file":
        response = read_file(data_json["file_path"])
    elif data_json["command"] == "response":
        response = file_editor.write_in_response(data_json["content"])
    elif data_json["command"] == "context":
        response = file_editor.write_in_context(
            data_json["prompt_title"], data_json["context"]
        )
        response.replace(workspace.path, "")
    elif data_json["command"] == "info":
        print(data_json["info"])
        response = "OK"
    elif data_json["command"] == "commit":
        response = workspace.commit(data_json["title"])
    response_dict = {"response": response}
    response_str = json.dumps(response_dict).encode(encoding="utf-8")
    try:
        client.send(response_str, "GET")
        resp = client.get_message()
    except Exception as e:
        print("Interrupted")
        exit()
