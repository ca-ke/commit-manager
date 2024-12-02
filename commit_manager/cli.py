import argparse
import ollama
import re
import json
from pathlib import Path
from commit_manager.commit_manager import CommitManager
from commit_manager.prompt_manager import PromptManager

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = f"{BASE_DIR}/config/prompts.toml"


def cli():
    parser = argparse.ArgumentParser(description="Manage Git Commits using local llm")
    parser.add_argument("repo_path", help="Path to the git Repo")

    subparsers = parser.add_subparsers(dest="command", required=True)

    commit_parser = subparsers.add_parser("commit", help="Commit staged cahnges.")
    commit_parser.add_argument("message", help="Commit message.")

    subparsers.add_parser(
        "generate_commit_message", help="Generate the commit message using Ollama"
    )

    subparsers.add_parser("current", help="Show the current branch")
    history_parser = subparsers.add_parser("history", help="Show the commit history")
    history_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of commits do display (default: 10",
    )

    args = parser.parse_args()
    client = ollama.Client()
    prompt_manager = PromptManager(PROMPT_FILE)
    manager = CommitManager(
        repo_path=args.repo_path,
        ollama_client=client,
        prompt_manager=prompt_manager,
    )

    if args.command == "commit":
        manager.commit_changes(args.message)
    elif args.command == "current":
        print(manager.get_current_branch())
    elif args.command == "generate_commit_message":
        commit_message = manager.generate_commit_message()
        json_match = re.search(r"{.*}", commit_message, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in the response")

        json_text = json.loads(json_match.group(0))
        manager.commit_changes(
            f"{json_text['type']}({json_text['scope']}): {json_text['description']}"
        )
    elif args.command == "history":
        history = manager.get_commit_history(limit=args.limit)
        for commit in history:
            print(f"Hash: {commit['hash']}")
            print(f"Author: {commit['author']}")
            print(f"Date: {commit['date']}")
            print(f"Message: {commit['message']}")


if __name__ == "__main__":
    cli()
