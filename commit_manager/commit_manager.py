import os
from git import Repo, GitCommandError


class CommitManager:
    def __init__(self, repo_path) -> None:
        if not os.path.exists(repo_path):
            raise FileNotFoundError(f"Repository path {repo_path} does not exists.")
        self.repo = Repo(repo_path)
        if self.repo.bare:
            raise ValueError(
                "The specifiedpath is a bare repository. Please provide a valid one"
            )

    def commit_changes(self, message: str) -> None:
        """
        Commit staged changes with the provide commit message
        """
        if not message.strip():
            raise ValueError("Commit message cannot be empty")
        try:
            self.repo.index.commit(message)
        except GitCommandError as e:
            raise RuntimeError(f"Falied to commit hanges: {e}")

    def get_current_branch(self) -> str:
        """
        Get the name of the current branch
        """
        return self.repo.active_branch.name

    def get_commit_history(self, limit=10):
        """
        Retrieve the latest commit history
        """
        try:
            commits = list(self.repo.iter_commits("HEAD", max_count=limit))
            return [
                {
                    "hash": commit.hexsha,
                    "author": commit.author.name,
                    "date": commit.committed_datetime,
                    "message": commit.message.strip(),
                }
                for commit in commits
            ]
        except GitCommandError as e:
            raise RuntimeError(f"Failed to retrieve commit history: {e}")
