import os
from settings import Settings
from workspace import Workspace

class FileEditor:

    def __init__(self, settings: Settings, workspace: Workspace):
        self.workspace = workspace
        self.response_dir = os.path.join(workspace.path, settings.response_dir)
        self.corrections_path = os.path.join(self.response_dir, "corrections.md")
        self.context_path = os.path.join(self.response_dir, "contexts/")
        self.fails_path = os.path.join(self.response_dir, "fails.md")
        self.response_path = os.path.join(self.response_dir, "response.md")
        if settings.existing_branch is None:
            os.makedirs(self.response_dir)
            os.makedirs(self.context_path)
        with open(self.corrections_path, 'w', encoding='utf-8'): pass
        with open(self.fails_path, 'w', encoding='utf-8'): pass
        with open(self.response_path, 'w', encoding='utf-8'): pass
        print(f"Response path: {self.response_path}")

    def write_in_response(self, data: str):
        if isinstance(data, str):
            self.safe_file_operation(self.response_path, 'a', data+"\n\n", "Cannot write in response file")
        else:
            for message in data:
                self.write_in_response(f"[{message[0]}] {message[1]}")
    
    def write_in_corrections(self, text: str):
        self.safe_file_operation(self.corrections_path, 'a', text+"\n\n", "Cannot write in corrections file")

    def write_in_fails(self, text: str):
        self.safe_file_operation(self.fails_path, 'a', text+"\n\n", "Cannot write in corrections file")

    def write_in_context(self, prompt_title: str, messages: list[tuple[str, str]]) -> str:
        path = os.path.join(self.context_path, prompt_title + ".md")
        text = ""
        for message in messages:
            text = text + f"[{message[0]}] {message[1]}\n\n"
        self.safe_file_operation(path, 'w', text+"\n\n",  f"Cannot write in context {prompt_title}")
        return path
        
    def write_in_workspace_file(self, rel_path: str, text: str) -> str:
        if rel_path not in self.workspace.files: return "Permission denied, file does not exist or you can't access and must assume is correct"
        self.safe_file_operation(rel_path, 'w', text, "Cannot write in workspace file")
        return "OK"
    
    def read_in_workspace_file(self, rel_path: str) -> str:
        if rel_path not in self.workspace.files: return "Permission denied, file does not exist or you can't access and must assume is correct"
        text = self.safe_file_operation(rel_path, 'r', None, "Cannot read a workspace file")
        return text
    
    def sanitize_path(self, filename: str) -> str:
        filename = filename.replace('..', '')
        if self.workspace.path in filename: return filename
        if filename.startswith('/'): filename = filename[1:]
        return os.path.join(self.workspace.path, filename)
    
    def safe_file_operation(self, rel_path, mode, text, exception_message):
        file_path = self.sanitize_path(rel_path)
        try:
            with open(file_path, mode, encoding='utf-8') as f:
                if mode in ['a', 'w', 'x']:
                    f.write(text)
                    f.flush()
                elif mode == 'r':
                    return f.read()
        except Exception as e:
            raise Exception(f"{exception_message}: {e}")
        
    
