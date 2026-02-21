import os, random, string, shutil

from settings import Settings
from gitBranch import GitBranch

class Workspace:

    """
    The program reaads the .gitignore file and ignore all files and directories found.
        .gitignore rules:
            - each does not start or end with '/'
            - '*' is not used
            - each line does not contain comments or extra characters
    """

    # files: list[str] = [] # Relative path of all files selected for IA
    # project_files: list[str] = [] # Absolute path for each project file
    # workspace_files: list[str] = [] # Absolute path for each workspace file

    def __init__(self, settings: Settings, source: str):
        # --------------------------------------------------------------
        # Inizializza le liste a livello di istanza (ognuna è isolata).
        # --------------------------------------------------------------
        self.files: list[str] = []
        self.project_files: list[str] = []
        self.workspace_files: list[str] = []
        self.settings = settings
        print(f"Source: {source}")
        self.branch = GitBranch(settings.workspace_path, source, settings.existing_branch, settings.job_name)
        self.path = os.path.join(settings.workspace_path, self.branch.branch_name)
        self.scan_files()          # Popola self.files, ecc.
        for file in self.files:
            workspace_file_path = os.path.join(self.path, file)
            self.workspace_files.append(workspace_file_path)
            print(f"Selected file: {file}")
        print(f"Workspace in {self.path}")

    def commit(self, commit_message: str) -> bool:
        return self.branch.commit(commit_message, self.workspace_files)
    
    def revert_commit(self):
        self.branch.revert_last_commit()
    
    def scan_files(self) -> None:
        """
        Scan all files to be considered.
        The method now *reset* the list before populating it, so a
        subsequent call does not accumulate stale entries.
        """
        # Reset the list each time the method is called
        self.files.clear()

        # Scan all files to be considered
        for root, dirs, files in os.walk(self.path):
            # Rimuove le directory da ignorare (definite in settings)
            dirs[:] = [d for d in dirs if d not in self.settings.ignore_elements]
            for filename in files:
                if filename in self.settings.ignore_elements:
                    continue
                # Add relative path to files list
                file_path = os.path.join(root, filename)
                filtered = os.path.relpath(file_path, self.path)
                self.files.append(filtered)
                