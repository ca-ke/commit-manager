import argparse

from commit_manager.commit_manager import CommitManager


def cli():
    parser = argparse.ArgumentParser(description="Manage Git Commits using local llm")
    parser.add_argument("repo_path", help="Path to the git Repo")

    subparsers = parser.add_subparsers(dest="command", required=True)

    commit_parser = subparsers.add_parser("commit", help="Commit staged cahnges.")
    commit_parser.add_argument("message", help="Commit message.")

    subparsers.add_parser("current", help="Show the current branch")
    history_parser = subparsers.add_parser("history", help="Show the commit history")
    history_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of commits do display (default: 10",
    )

    args = parser.parse_args()
    manager = CommitManager(args.repo_path)

    if args.command == "commit":
        manager.commit_changes(args.message)
    elif args.command == "current":
        print(manager.get_current_branch())
    elif args.command == "history":
        history = manager.get_commit_history(limit=args.limit)
        for commit in history:
            print(f"Hash: {commit['hash']}")
            print(f"Author: {commit['author']}")
            print(f"Date: {commit['date']}")
            print(f"Message: {commit['message']}")


if __name__ == "__main__":
    cli()
