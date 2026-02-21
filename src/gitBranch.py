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
        """
        Aggiunge i file indicati all’indice e, se ci sono effettive modifiche,
        effettua il commit. Restituisce True se il commit è stato eseguito,
        False altrimenti.
        """
        self.repo.index.add(files)

        # Git restituisce una stringa vuota quando non ci sono differenze.
        # Usare una verifica di “empty string” è più affidabile di cercare '.'
        staged_changes = self.git_cmd.diff("--cached", "--name-only")
        if not staged_changes:          # Nessuna modifica da committare
            return False

        self.repo.index.commit(commit_message)
        print("Commit done")
        return True
    
    def revert_last_commit(self) -> bool:
        """
        Revert the repository to the previous commit.
        Returns ``True`` if the reset succeeded, ``False`` otherwise.
        """
        try:
            # Ottieni l'ID dell'ultimo commit (prima della revert)
            # ``git log -n 1 --oneline`` restituisce qualcosa come
            # ``abcd1234 Messaggio``; ne prendiamo il primo token.
            log_output = self.repo.git.log("-n", "1", "--oneline")
            commit_id = log_output.split()[0]

            print(f"[COMMIT] revert to commit id {commit_id}")

            # Esegui il reset hard al commit individuato.
            self.repo.git.reset("--hard", commit_id)
            return True
        except Exception as e:
            # In caso di errore, forniamo un messaggio più chiaro.
            raise Exception(f"Failed to revert last commit: {e}")