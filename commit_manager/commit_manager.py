import os
from ollama import Client
from typing import Dict
from git import Repo, GitCommandError

from commit_manager.prompt_manager import PromptManager


class CommitManager:
    def __init__(
        self,
        repo_path,
        ollama_client: Client,
        prompt_manager: PromptManager,
    ) -> None:
        if not os.path.exists(repo_path):
            raise FileNotFoundError(f"Repository path {repo_path} does not exists.")
        self.repo = Repo(repo_path)
        if self.repo.bare:
            raise ValueError(
                "The specifiedpath is a bare repository. Please provide a valid one"
            )
        self.prompt_manager = prompt_manager
        self.ollama_client = ollama_client

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

    def generate_commit_message(self) -> str:
        """
        Generate a commit message based on staged file content using Ollama
        """
        if not self.prompt_manager or not self.ollama_client:
            print(self.prompt_manager)
            print(self.ollama_client)
            raise ValueError("PromptManager and Ollama Client must be configured")

        staged_files = self._get_staged_files()
        if not staged_files:
            return "No files staged for commit"

        if len(staged_files) == 1:
            file_name, file_content = next(iter(staged_files.items()))
            prompt_template = self.prompt_manager.get_prompt(
                "file_based_commit", "single_file"
            )
            if prompt_template is not None:
                prompt = prompt_template.replace("{{ file_name }}", file_name).replace(
                    "{{ file_content }}", file_content
                )
            else:
                raise ValueError("Prompt not found")
        else:
            raise NotImplementedError("This type is not implemented yet")

        response = self.ollama_client.chat(
            model="llama3.2",
            messages=[{"role": "system", "content": prompt}],
        )

        return response["text"]

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

    def _get_staged_files(self) -> Dict[str, str]:
        """
        Retrieve staged files and their content
        """
        staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
        staged_files_content = {}

        for file in staged_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    staged_files_content[file] = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file, "r", encoding="iso-8859-1") as f:
                        staged_files_content[file] = f.read()
                except Exception as e:
                    print(f"Warning: Could not read file '{file}'. The issue {e}")
                    staged_files_content[file] = (
                        "[Unreadable file due to enconding issues]"
                    )
        return staged_files_content
