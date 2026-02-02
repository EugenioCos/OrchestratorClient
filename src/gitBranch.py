import os, random, string
from git import Repo

class GitBranch:

    def __init__(self, workspace_path: str, source: str, branch_name: str | None, name_start: str):
        if branch_name is None:
            random_id = ''.join(random.choices(string.digits, k=4))
            self.branch_name = f"{name_start}_{random_id}"
            os.mkdir(os.path.join(workspace_path, self.branch_name))
            dest_path = os.path.join(workspace_path, self.branch_name)
            self.repo = Repo.clone_from(source, dest_path)
            self.git_cmd = self.repo.git
            self.git_cmd.checkout("HEAD", b=self.branch_name) # Create a new branch.
        else:
            self.branch_name = branch_name
            git_path = os.path.join(workspace_path, branch_name, ".git/")
            self.repo = Repo(git_path)
            self.git_cmd = self.repo.git

    def commit(self, commit_message: str, files: list[str]) -> bool:
        self.repo.index.add(files)
        if '.' not in self.git_cmd.diff("--cached", "--name-only"):
            return False
        self.repo.index.commit(commit_message)
        print("Commit done")
        return True