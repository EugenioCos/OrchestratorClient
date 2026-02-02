import os, socket, json

from settings import Settings
from workspace import Workspace
from fileEditor import FileEditor

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432 # Port to listen on (non-privileged ports are > 1023)

settings = Settings("settings.json")
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

workspace = Workspace(settings, settings.source)
#workspace.commit("existing changes")
file_editor = FileEditor(settings, workspace)

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
    
# Listen all data and log / execute it
def start_listening(s, reader):
    while(True):
        data = reader.readline()
        data_json = json.loads(data)
        print(f"[COMMAND] {data_json["command"]}")
        response = None
        if(data_json["command"] == 'replace_in_file'):
            response = replace_in_file(data_json["file_path"], data_json["old"], data_json["new"])
        elif(data_json["command"] == 'write_in_file'):
            response = write_in_file(data_json["file_path"], data_json["text"])
        elif(data_json["command"] == 'list'):
            response = workspace.files
        elif(data_json["command"] == 'read_file'):
            response = read_file(data_json["file_path"])
        elif(data_json["command"] == 'response'):
            response = file_editor.write_in_response(data_json["content"])
        elif(data_json["command"] == 'context'):
            response = file_editor.write_in_context(data_json["prompt_title"], data_json["context"])
            response.replace(workspace.path, '')
        elif(data_json["command"] == 'info'):
            print(data_json["info"])
            response = "OK"
        elif(data_json["command"] == 'commit'):
            response = workspace.commit(data_json["title"])
        response_dict = { "response": response }
        response_str = json.dumps(response_dict).encode(encoding="utf-8")
        s.sendall(bytearray(response_str)+b'\n')
    

# Send request to server with model, settings and job

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"[CONNECTION] Connected")
    s.sendall(bytearray(data_for_server)+b'\n')
    reader = s.makefile('r', encoding='utf-8')
    data = reader.readline().strip()
    if data == "OK":
        print("[SERVER] Job started", flush=True)
        start_listening(s, reader)
    print(data)
